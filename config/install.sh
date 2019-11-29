# Run from the root directory with ./config/install.sh
# Note that pre-commit is not in the requirements.txt, as we don't want this to ship with the package.

python -m venv env
source env/bin/activate
pip install -r requirements-dev.txt
cd config || exit
pre-commit install
cd ..
