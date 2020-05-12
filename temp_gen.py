# this file just generates a list of feasible experiments to run (BDP > 20)
# so we can manually distribute them amongst the clusters
MTU = 1502
allowed_exps = []
# 1000, 7000 on umass
for flows in [100, 500, 2000, 5000, 10000]:
# for flows in [200, 700]:
    for q_bdp in [1/flows**0.5/10, 1/flows**0.5, 2, 6]:
#     for q_bdp in [1/flows**0.5, 2, 6]:
        for bw in [100, 1024, 10240]:
            for edgeDel2 in [5, 10, 20, 25, 35, 50]:
                for randSeed in range(1000, 10001, 1000):
                    fair_bdp_pkts = 7 * bw * 1024 * 1024 * 0.02 / 8 / flows / MTU
                    if fair_bdp_pkts < 10:
                        continue
                    allowed_exps.append((flows, bw, edgeDel2, q_bdp))
                    print(rf'echo "cd ns-allinone-3.30.1/ns-3.30.1 && ./waf --run-no-build \"dumbbell-p2p --nodes=100 --flows={flows} --simTime=610 --edgeDelay1=5 --edgeDelay2={edgeDel2} --btlSpeedMbps={bw} --edgeSpeedMbps={bw} --bdpFactor={"%g" % q_bdp} --randSeed={randSeed}\""')
print(len(allowed_exps))
pass