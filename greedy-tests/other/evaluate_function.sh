TEST_NAME="plot"

export ROOT_LOCATION="$(pwd)"

ASTE_LOCATION="${ROOT_LOCATION}/../aste" # CHANGE DEPENDING ON ASTE INSTALLATION

RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
ASTE_SRC="${ASTE_LOCATION}/src"
export PATH=$ASTE_BUILD:$PATH

python3 "${ASTE_SRC}/precice-aste-evaluate" -m "${ROOT_LOCATION}/meshes/t_0.01.vtk" -f "scaled-eggholder3d" -d "scaled Eggholder" -o "eval.vtk" -dir "${ROOT_LOCATION}"
python3 "${ASTE_SRC}/precice-aste-evaluate" -m "eval.vtk" -f "0.78 + cos(10*(x+y+z))" -d "scaled cos" -o "eval.vtk" -dir "${ROOT_LOCATION}"
python3 "${ASTE_SRC}/precice-aste-evaluate" -m "eval.vtk" -f "franke3d" -d "Franke" -o "eval.vtk" -dir "${ROOT_LOCATION}"