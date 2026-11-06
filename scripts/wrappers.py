from bluemath_tk.wrappers.swash.swash_wrapper import SwashModelWrapper
from bluemath_tk.waves.series import waves_dispersion
import numpy as np
import os.path as op
from scripts.bathymetry import linear_profile

class SwashModelWrapper_ondas(SwashModelWrapper):
    """
    Wrapper for the SWASH model with vegetation.
    """

    def build_case(self, case_context: dict, case_dir: str) -> None:
        super().build_case(case_context=case_context, case_dir=case_dir)

        # Save depth.bot
        np.savetxt(op.join(case_dir, "depth.bot"), self.depth_array)
 
class SwashModelWrapper_friction(SwashModelWrapper):
    """
    Wrapper for the SWASH model with vegetation.
    """
    def build_case(self, case_context: dict, case_dir: str) -> None:

        super().build_case(case_context=case_context, case_dir=case_dir)

        # Save depth.bot
        np.savetxt(op.join(case_dir, "depth.bot"), self.depth_array)

        friction_array = np.zeros(len(self.depth_array))

        pos_ini = case_context['pos_ini']
        pos_fin = case_context['pos_fin']
        
        friction_array[pos_ini:pos_fin] = friction_array[pos_ini:pos_fin] + case_context['friction_coef']
        np.savetxt(op.join(case_dir, 'friction.txt'), friction_array)

class SwashModelWrapper_shoaling(SwashModelWrapper):
    """
    Wrapper for the SWASH model with vegetation.
    """

    def build_case(
        self,
        case_context: dict,
        case_dir: str,
    ) -> None:
        """
        Build the input files for a case.

        Parameters
        ----------
        case_context : dict
            The case context.
        case_dir : str
            The case directory.
        """
        # Build the input waves
        waves_dict = {
            "H": case_context["Hs"],
            "T": np.sqrt(
                (case_context["Hs"] * 2 * np.pi)
                / (self.gravity * case_context["Hs_L0"])
            ),
            "warmup": case_context["warmup"],
            "comptime": case_context["comptime"],
            "gamma": case_context["gamma"],
            "deltat": case_context["deltat"],
        }
        case_context["waves_dict"] = waves_dict

        # Define the peak period
        case_context["Tp"] = waves_dict["T"]

        _, depth_array = linear_profile(h0=case_context['h0'], Ltotal=case_context['Ltotal'], Wconst=case_context['Wfore'], slope=case_context['m'])
        depth_array = - depth_array
        self.depth_array = depth_array
        # Calculate computational parameters
        # Assuming there is always 1m of setup due to (IG, VLF)
        L1, _k1, _c1 = waves_dispersion(T=waves_dict["T"], h=1.0)
        _L, _k, c = waves_dispersion(T=waves_dict["T"], h=depth_array[0])
        dx = L1 / case_context["n_nodes_per_wavelength"]

        # Computational time step
        deltc = 0.5 * dx / (np.sqrt(self.gravity * depth_array[0]) + np.abs(c))
        # Computational grid modifications
        mxc = int(self.mxinp / dx)

        # Update the case context
        case_context["mxc"] = mxc
        case_context["deltc"] = deltc

        # Save depth.bot
        np.savetxt(op.join(case_dir, "depth.bot"), depth_array)