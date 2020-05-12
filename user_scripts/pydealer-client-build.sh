# build ns-3 here
cd ns-allinone-3.30.1/ns-3.30.1 || exit 1
./waf configure -d optimized --enable-static # configure the build!
./waf # build the build!