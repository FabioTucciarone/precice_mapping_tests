TEST_NAME="cholesky-vs-cut"

export ROOT_LOCATION="$(pwd)"

ASTE_PATH="${ROOT_LOCATION}/../aste"                     # CHANGE DEPENDING ON ASTE INSTALLATION
HEAPTRACK_PATH="${ROOT_LOCATION}/../heaptrack/build/bin" # CHANGE DEPENDING ON HEAPTRACK INSTALLATION

RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
ASTE_BUILD="${ASTE_PATH}/build"
PATH=$ASTE_BUILD:$HEAPTRACK_PATH:$PATH

rm -rf $TEST_LOCATION
mkdir -p $TEST_LOCATION

echo ""
echo "[TEST] precice-aste-evaluate"
echo ""

cd $TEST_LOCATION

# Calculate franke function on fine mesh
precice-aste-evaluate -m "${ROOT_LOCATION}/meshes/t_0.006.vtk" -f "franke3d" -d "Franke Function" -o "${TEST_LOCATION}/mesh_A.vtk"

echo ""
echo "[TEST] precice-aste-run"
echo ""

# Map from the finer mesh to coarser mesh
precice-aste-run -v -p A --mesh "mesh_A" --data "Franke Function" -c "${RUN_LOCATION}/precice-config.xml" &
heaptrack precice-aste-run -v -p B --mesh "${ROOT_LOCATION}/meshes/t_0.008" --output "mesh_B" --data "InterpolatedData" -c "${RUN_LOCATION}/precice-config.xml"

echo ""
echo "[TEST] precice-aste-evaluate"
echo ""

# Calculate statistics
precice-aste-evaluate -m "mesh_B.vtk" -f "franke3d" -d difference --diffdata "InterpolatedData" --diff

cd "${ROOT_LOCATION}"
