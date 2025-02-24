# CI

## Overview

This project is designed to automate the process of analyzing latest releases and nightly builds of various SMT solvers for potential bugs. By leveraging GitHub Actions, this project ensures that the solvers are regularly checked and any issues are promptly identified. This initiative was developed by Andrei Zhukov and Dominik Winterer as part of a semester project at the AST Lab, ETH Zurich.

## Solvers Monitored

The project focuses on the following SMT solvers:

### Latest Stable Releases
- **Z3**
- **CVC5**
- **OpenSMT2**
- **Yices2**
- **MathSAT5**
- **Ostrich**
- **SMT-RAT**
- **STP**

### Nightly Builds
- **Z3**
- **CVC5**

## How It Works

1. **GitHub Actions**: The project utilizes GitHub Actions to automate the process. Workflows are scheduled to run weekly, ensuring consistent monitoring of the solvers.

2. **Stable Release Checks**: For each solver listed under stable releases, the latest stable version is fetched and analyzed for bugs.

3. **Nightly Build Checks**: Nightly builds of Z3 and CVC5 are also fetched and scrutinized to catch any issues that might arise in the latest development versions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or further information, please contact the developers:

- **Andrei Zhukov**
- **Dominik Winterer**

Developed at the AST Lab, ETH Zurich.
