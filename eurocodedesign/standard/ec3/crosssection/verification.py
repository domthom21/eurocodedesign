""" 
    Module for general verification classes, definitions and constants
        - general verification procedures: should return an instance of 
          VerificationData
"""
from dataclasses import dataclass
from typing import Dict
from math import sqrt

from eurocodedesign.geometry import steelsections as ss # type: ignore

GAMMA_M0 = 1.0

@dataclass
class Verification:
    check_tag: str  # unique string that identifies what type of check was performed
    passes: bool  # was the check passed or not
    eta: float | None # utilisation ration for strength check o.w. None
    check_data: Dict  # additional information relevant for print_out / saving
    

@dataclass
class VerificationData:
    # container for all of the checks (instances of Verification) performed on 
    # an element
    tag: int  # element tag etc
    
    def __post_init__(self):
        self.checks = []   # a list of the checks performed on the element
        self.passes = False   # True if all of the added checks pass
        
    def add_check(self, check: Verification):
        self.checks.append(check)
        self.passing()
      
    def passing(self):
        self.passes = all([c.passes for c in self.checks])


def section_N(section: ss.SteelSection, N_Ed: float, 
                     fy: float) -> Verification:
    N_Rd = section.A * fy / GAMMA_M0
    eta = abs(N_Ed / N_Rd)
    check_data = {"N_Ed": N_Ed,
                  "N_Rd": N_Rd,
                  "eta": eta,
                  "section": section}
    
    vd = Verification("section_N", eta <= 1.0, eta, check_data)
    return vd
   

def section_V_z(section: ss.SteelSection, V_z_Ed: float, 
                       fy: float) -> VerificationData:
    V_z_Rd = section.A_vz * fy / GAMMA_M0 / sqrt(3)
    eta = abs(V_z_Ed / V_z_Rd)
    check_data = {"V_z_Ed": V_z_Ed,
                  "V_z_Rd": V_z_Rd,
                  "eta": eta,
                  "section": section}
    vd = Verification("section_V_z", eta <= 1.0, eta, check_data)
    return vd


def section_M_ply(section: ss.SteelSection, M_ply_Ed: float, 
                         fy: float) -> VerificationData:
    M_ply_Rd = section.W_ply * fy / GAMMA_M0
    eta = abs(M_ply_Ed / M_ply_Rd)
    check_data = {"M_ply_Ed": M_ply_Ed,
                  "M_ply_Rd": M_ply_Rd,
                  "eta": eta,
                  "section": section}
    vd = Verification("section_M_ply", eta <= 1.0, eta, check_data)
    return vd
    

def section_MNV_interaction(section: ss.ISection, M_y_Ed: float,
                            V_z_Ed: float, N_Ed: float, 
                            fy: float) -> Verification:
    # only implemented for doubly symmetric I-Sections
    check_data = {}
    check_data["section"] = section
    
    N_Ed = abs(N_Ed)
    V_z_Ed = abs(V_z_Ed)
    M_y_Ed = abs(M_y_Ed)   # ok for I-sections as they are symmetric
    
    A_vz = section.A_vz
    A = section.A
    W_ply = section.W_ply

    tf = section.t_f
    tw = section.t_w
    b = section.b
    hw = section.h - 2 * section.t_f

    V_plz_Rd = A_vz * fy / sqrt(3) / GAMMA_M0
    N_pl_Rd = A * fy / GAMMA_M0
    M_ply_Rd = W_ply * fy / GAMMA_M0
    
    vd_N = section_N(section, N_Ed, fy)
    vd_V_z = section_V_z(section, V_z_Ed, fy)
    vd_M_y = section_M_ply(section, M_y_Ed, fy)
    
    check_data["N_Ed"] = N_Ed
    check_data["N_Rd"] = N_pl_Rd
    check_data["eta_N"] = vd_N.eta
    check_data["V_z_Ed"] = V_z_Ed
    check_data["V_plz_Rd"] = V_plz_Rd
    check_data["eta_V_z"] = vd_V_z.eta              
    check_data["M_y_Ed"] = M_y_Ed
    check_data["M_ply_Rd"] = M_ply_Rd
    check_data["eta_M_y"] = vd_M_y.eta

    
    if not all([vd_N.passes, vd_V_z.passes, vd_M_y.passes]):
        eta = max([vd_N.eta, vd_V_z.eta, vd_M_y.eta])
        vd = Verification("section_MNV_interaction", False, 
                           eta, check_data)
        return vd
    
    
    if V_z_Ed <= 0.5 * V_plz_Rd:
        check_data["V_interaction"] = False
        if N_Ed > min(0.25 * N_pl_Rd, 0.5 * hw * tw * fy / GAMMA_M0):
            n = N_Ed / N_pl_Rd
            a = min((A - 2 * b * tf) / A, 0.5)
            M_ny_Rd = min(M_ply_Rd *(1 - n) / (1 - 0.5 * a), M_ply_Rd)
            
            check_data["N_interaction"] = True
            check_data["N_reduction"] = (1 - n) / (1 - 0.5 * a)
        else:
            check_data["N_interaction"] = False
            M_ny_Rd = M_ply_Rd
               
        eta = M_y_Ed / M_ny_Rd
        check_data["eta_M_ny_Rd"] = eta
        
        vd = Verification("section_MNV_interaction", eta < 1.0, 
                          eta, check_data)
        return vd
        
    else:
        
        rho = min(max(0, (2 * V_z_Ed / V_plz_Rd -1) ** 2), 1.0)
        # method (b) from Schneider Bautabellen flowchart on page 8.18
        M_vy_Rd = (W_ply - rho * A_vz ** 2 / (4 * tw)) * fy / GAMMA_M0
        a_vz = A_vz / A
        N_v_Rd = N_pl_Rd * (1 - a_vz * rho)
    
        check_data["V_interaction"] = True
        check_data["rho"] = rho
        check_data["M_vy_Rd"] = M_vy_Rd
        check_data["a_vz"] = a_vz
        check_data["N_v_Rd"] = N_v_Rd
        
        if N_Ed > min(0.25 * N_v_Rd, hw * tw * fy * (1-rho) / (2 * GAMMA_M0)):
            nv = N_Ed / N_v_Rd
            A_red = A - A_vz * rho
            a_red = min((A_red - 2 * b * tf) / A_red, 0.5)
            M_nvy_Rd = min(M_vy_Rd * (1 - nv) / (1 - 0.5 * a_red), M_vy_Rd)
            
            check_data["N_interaction"] = True
            check_data["N_reduction"] = (1 - nv) / (1 - 0.5 * a_red)
        else:
            check_data["N_interaction"] = False
            M_nvy_Rd = M_vy_Rd
        
        eta = M_y_Ed / M_nvy_Rd
        check_data["eta_M_nvy_Rd"] = eta
        
        vd = Verification("section_MNV_interaction", eta < 1.0, 
                           eta, check_data)
        return vd  