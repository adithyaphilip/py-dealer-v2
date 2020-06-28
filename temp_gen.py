# this file just generates a list of feasible experiments to run (BDP > 20)
# so we can manually distribute them amongst the clusters
MTU = 1502
allowed_exps = []
SIM_TIME_S = 1210
mean_rand_pico = 5000
cca = 0
# 1000, 7000 on umass
for flows in reversed([2, 10, 20, 50, 100, 150, 200, 250, 300, 400, 500, 700, 1000, 2000, 4000, 5000, 8000, 10000]):
    for udp_bw_frac in [0.10]:
        # for flows in [200, 700]:
        for q_bdp in [1 / flows ** 0.5, 0.1 / flows ** 0.5]:
            #     for q_bdp in [1/flows**0.5, 2, 6]:
            for bw in [int(10240 * flows / 10000) if flows > 100 else 100]:
                for edgeDel2 in [5, 10, 22, 33, 43, 55]:
                    for randSeed in range(1, 11, 1):
                        # fair_bdp_pkts = 7 * bw * 1024 * 1024 * 0.02 / 8 / flows / MTU
                        # if fair_bdp_pkts < 10:
                        #     continue
                        allowed_exps.append((flows, bw, edgeDel2, q_bdp))
                        print(
                            rf'echo "cd ns-allinone-3.30.1/ns-3.30.1 && ./waf --run-no-build \"dumbbell-p2p --nodes={min(flows, 100)} --flows={flows} --simTime={SIM_TIME_S} --edgeDelay1=5 --edgeDelay2={edgeDel2} --btlSpeedMbps={bw} --edgeSpeedMbps={bw} --bdpFactor={"%g" % q_bdp} --randSeed={randSeed}  --meanRandPico={mean_rand_pico} --udpBwFrac={udp_bw_frac} --cca={cca}\""')
print(len(allowed_exps))
pass
