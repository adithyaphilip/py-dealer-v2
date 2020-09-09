# build ns-3 here
cd ns-3-dev || exit 1
./waf configure -d optimized --enable-static # configure the build!
./waf # build the build!