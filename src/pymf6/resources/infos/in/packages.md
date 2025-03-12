#### Model packages

Packages can be accessed via `model.packages.package_name`.
If `package_name` is not a valid Python identifier, access with
pandas logic `model.packages.loc['package_name']`.
Packages that are mutable (`is_mutable` is True) can be converted in a
mutable boundary condition with `.as_mutable_bc()`.