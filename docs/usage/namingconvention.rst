=================
Naming convention
=================

The naming convention in eurocodedesign tries to follow the eurocode naming convention as closely as possible, while
being restrained to valid python names and using only alphanumerical characters.

* First letter is uppercase if the symbol is uppercase in eurocode, e.g. ``F_Ed``
* Commas in subscript are neglected, except for ``Ed`` and ``Rd``, where it is replaced by an underscore, e.g. ``F_z_Ed, M_BV_Rd, M_cB_Rd, M_pl_Rd``
* Subscript is added with an underscore before the subscript, e.g. ``M_I_Ed``
* Only alphanumerical names are valid, greek letters are written out, e.g. ``Delta_M_y_Ed, Phi_LT, alpha_crop, alpha_ultk``
* Variable names with a bar, like relative slenderness, are written as ``bar_lambda_czmod``
* Other examples are ``phi_0, Chi_LT, psi``

