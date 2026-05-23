import os
from pathlib import Path

from matplotlib import pyplot as plt

plt.rcParams["font.family"] = "STIXGeneral"

from core.visualization_core.visualization import PlotLine, TU_COLORS, plot_moment_curvature_multiple, mirror_plot

# ─── Data ────────────────────────────────────────────────

m_kappa_c1_3_support = {
    "NONE_PARABOLIC": {
        "kappa": [0.00001, 0.000451, 0.000891, 0.001332, 0.001772, 0.002213, 0.002653, 0.003094, 0.003534, 0.003975, 0.004415, 0.004856, 0.005296, 0.005737, 0.006177, 0.006618, 0.007058, 0.007499, 0.007939, 0.00838, 0.008821, 0.009261, 0.009702, 0.010142, 0.010583, 0.011023, 0.011464, 0.011904, 0.012345, 0.012785, 0.013226, 0.013666, 0.014107, 0.014547, 0.014988, 0.015428, 0.015869, 0.016309, 0.01675, 0.017191, 0.022821],
        "moment": [0.1137, 5.1206, 10.1276, 15.1345, 20.1415, 25.1484, 30.1553, 35.1541, 40.1274, 45.0772, 50.0116, 54.9357, 59.8527, 64.7601, 69.6501, 74.5195, 79.3686, 84.2009, 89.0195, 93.8224, 98.6054, 103.3666, 108.1052, 112.8216, 117.5173, 122.1897, 126.8362, 131.4555, 136.0471, 140.6108, 145.144, 149.6436, 154.1077, 158.5353, 162.9258, 167.2767, 171.5821, 175.8382, 180.0432, 184.1957, 229.3571],
    },
    "TENSTIFF_PARABOLIC": {
        "kappa":  [0, 0.00001, 0.000447547, 0.000885094, 0.001322642, 0.001760189, 0.002197736, 0.002635283, 0.00307283, 0.003510377, 0.003947925, 0.00463638, 0.004823019, 0.005260566, 0.005698113, 0.00613566, 0.006573208, 0.007010755, 0.007448302, 0.007885849, 0.008323396, 0.008760943, 0.009198491, 0.009636038, 0.010073585, 0.010511132, 0.010948679, 0.011386226, 0.011823774, 0.012261321, 0.012698868, 0.013136415, 0.013573962, 0.014011509, 0.014449057, 0.014886604, 0.015324151, 0.015761698, 0.016199245, 0.016636792, 0.01707434],
        "moment": [0, 0.85975027, 38.32503965, 55.0838003, 57.5420522, 57.5420522, 57.5420522, 57.5420522, 57.5420522, 57.5420522, 57.5420522, 57.5420522, 59.14446428, 63.20182998, 67.45146083, 71.82836694, 76.29117039, 80.81225046, 85.37245717, 89.95806708, 94.55892732, 99.16732681, 103.777226, 108.383782, 112.982981, 117.571422, 122.146138, 126.7044502, 131.2438975, 135.76215, 140.2569442, 144.7260525, 149.1672156, 153.5781184, 157.9563623, 162.299403, 166.604539, 170.868854, 175.0891803, 179.262053, 183.3836386],
    },
    "FCTM_PARABOLIC": {
        "kappa": [0.00001, 0.000450726, 0.000891452, 0.001332178, 0.001772904, 0.00221363, 0.002654356, 0.003372925, 0.003535808, 0.003976534, 0.00441726, 0.004857986, 0.005298712, 0.005739439, 0.006180165, 0.006620891, 0.007061617, 0.007502343, 0.007943069, 0.008383795, 0.008824521, 0.009265247, 0.009705973, 0.010146699, 0.010587425, 0.011028151, 0.011468877, 0.011909603, 0.012350329, 0.012791055, 0.013231781, 0.013672507, 0.014113233, 0.014553959, 0.014994685, 0.015435411, 0.015876137, 0.016316864, 0.01675759, 0.017198316, 0.017763224, 0.018328133, 0.018893041, 0.01945795, 0.020022858, 0.020587766, 0.021152675, 0.021717583, 0.022282492, 0.0228474],
        "moment": [0.85975027, 38.5955178, 38.5955178, 38.5955178, 38.5955178, 38.5955178, 38.5955178, 38.5955178, 40.4085627, 45.3238384, 50.2393896, 55.1499016, 60.0520508, 64.9435716, 69.8227929, 74.6884011, 79.5392685, 84.3743938, 89.1928365, 93.9936834, 98.7760201, 103.538922, 108.281424, 113.002533, 117.701191, 122.376289, 127.026631, 131.650946, 136.247871, 140.815935, 145.353537, 149.858956, 154.330304, 158.765529, 163.162371, 167.518349, 171.830731, 176.096476, 180.312202, 184.474127, 189.723202, 194.866521, 199.891865, 204.784624, 209.527081, 214.097433, 218.46835, 222.604821, 226.460822, 229.973826],
    },
    "ELASTIC_ELASTIC": {
        "kappa": [0.00001, 0.00404612, 0.00808224, 0.01211836, 0.016154479, 0.020190599, 0.024226719, 0.028262839, 0.032298959, 0.036335079, 0.040371199, 0.044407318, 0.048443438, 0.052479558, 0.056515678, 0.060551798, 0.064587918, 0.068624038, 0.072660157, 0.076696277, 0.080732397, 0.084768517, 0.088804637, 0.092840757, 0.096876877, 0.100912996, 0.104949116, 0.108985236, 0.113021356, 0.117057476, 0.121093596, 0.125129716, 0.129165835, 0.133201955, 0.137238075, 0.141274195, 0.145310315, 0.149346435, 0.153382555, 0.157418674],
        "moment": [0.838103288, 339.106718, 677.375333, 1015.64395, 1353.91256, 1692.18118, 2030.44979, 2368.71841, 2706.98702, 3045.25564, 3383.52425, 3721.79287, 4060.06148, 4398.3301, 4736.59871, 5074.86732, 5413.13594, 5751.40455, 6089.67317, 6427.94178, 6766.2104, 7104.47901, 7442.74763, 7781.01624, 8119.28486, 8457.55347, 8795.82209, 9134.0907, 9472.35932, 9810.62793, 10148.8965, 10487.1652, 10825.4338, 11163.7024, 11501.971, 11840.2396, 12178.5082, 12516.7768, 12855.0455, 13193.3141],
    },
    "FACTOR_METHOD": {
        "kappa": [1.35663e-06, 6.10975e-05, 0.000120839, 0.00018058, 0.000240322, 0.000300063, 0.000359804, 0.000419448, 0.000478788, 0.002390698, 0.002985188, 0.003552392, 0.004098082, 0.004628346, 0.005144869, 0.005651769, 0.006149411, 0.006641065, 0.007126222, 0.007607482, 0.008084625, 0.00855731, 0.009027836, 0.009494789, 0.009960369, 0.010422971, 0.010884682, 0.01134382, 0.011802451, 0.012258834, 0.012714986, 0.013169097, 0.013623177, 0.014075396, 0.01452776, 0.0149784, 0.015429285, 0.015878523, 0.016328104, 0.016777106, 0.022463409],
        "moment": [0.1137, 5.1206, 10.1276, 15.1345, 20.1415, 25.1484, 30.1553, 35.1541, 40.1274, 45.0772, 50.0116, 54.9357, 59.8527, 64.7601, 69.6501, 74.5195, 79.3686, 84.2009, 89.0195, 93.8224, 98.6054, 103.3666, 108.1052, 112.8216, 117.5173, 122.1897, 126.8362, 131.4555, 136.0471, 140.6108, 145.1440, 149.6436, 154.1077, 158.5353, 162.9258, 167.2767, 171.5821, 175.8382, 180.0432, 184.1957, 229.3571],
    },
}


m_kappa_c1_3_midspan = {
    "NONE_PARABOLIC": {
        "kappa": [0.00001, 0.000387, 0.000764, 0.001141, 0.001518, 0.001895, 0.002272, 0.002649, 0.003026, 0.003403, 0.00378, 0.004157, 0.004534, 0.004911, 0.005288, 0.005665, 0.006042, 0.006419, 0.006796, 0.007173, 0.00755, 0.007927, 0.008304, 0.00868, 0.009057, 0.009434, 0.009811, 0.010188, 0.010565, 0.010942, 0.011319, 0.011696, 0.012073, 0.01245, 0.012827, 0.013204, 0.013581, 0.013958, 0.014335, 0.014712, 0.019431],
        "moment": [0.2152, 8.3273, 16.4394, 24.5515, 32.6637, 40.7758, 48.8879, 56.988, 65.0496, 73.0783, 81.086, 89.0796, 97.0633, 105.0336, 112.978, 120.891, 128.7748, 136.6354, 144.4772, 152.2971, 160.088, 167.846, 175.5697, 183.2616, 190.9249, 198.5552, 206.1477, 213.6998, 221.21, 228.6783, 236.1032, 243.4797, 250.8041, 258.074, 265.288, 272.4417, 279.5279, 286.5416, 293.479, 300.337, 374.3411],
    },
    "TENSTIFF_PARABOLIC": {
        "kappa": [0.00001, 0.000384347, 0.000758694, 0.001133041, 0.001507388, 0.001881735, 0.002256082, 0.002630429, 0.003004776, 0.003379123, 0.00375347, 0.004127817, 0.004502164, 0.004876511, 0.005250858, 0.005625205, 0.005999552, 0.006373899, 0.006748246, 0.007122593, 0.00749694, 0.007871287, 0.008245634, 0.008619981, 0.008994328, 0.009368675, 0.009743022, 0.010117369, 0.010491716, 0.010866063, 0.01124041, 0.011614757, 0.011989104, 0.012363451, 0.012737798, 0.013112145, 0.013486492, 0.013860839, 0.014235186, 0.014609533, 0.015085539, 0.015561544, 0.01603755, 0.016513556, 0.016989561, 0.017465567, 0.017941573, 0.018417578, 0.018893584, 0.01936959],
        "moment": [0.901559514, 34.5415371, 57.5292923, 65.8538517, 69.9768148, 72.9566631, 75.9769812, 78.732695, 81.2511608, 84.0907227, 89.0411648, 95.1567797, 101.813976, 108.790291, 115.969208, 123.281465, 130.682712, 138.143031, 145.641384, 153.162438, 160.694645, 168.229053, 175.758495, 183.277071, 190.779789, 198.262266, 205.720568, 213.151069, 220.550302, 227.914908, 235.241542, 242.526818, 249.767231, 256.959119, 264.098591, 271.181484, 278.203273, 285.159022, 292.043278, 298.849981, 307.38232, 315.762113, 323.970299, 331.983997, 339.775292, 347.309493, 354.542603, 361.417378, 367.857064, 373.754664],
    },
    "FCTM_PARABOLIC": {
        "kappa": [0.00001, 0.000387162, 0.000764324, 0.001141486, 0.001552575, 0.00189581, 0.002272972, 0.002650134, 0.003027296, 0.003404458, 0.00378162, 0.004158782, 0.004535944, 0.004913105, 0.005290267, 0.005667429, 0.006044591, 0.006421753, 0.006798915, 0.007176077, 0.007553239, 0.007930401, 0.008307563, 0.008684725, 0.009061887, 0.009439049, 0.009816211, 0.010193373, 0.010570535, 0.010947697, 0.011324859, 0.011702021, 0.012079183, 0.012456345, 0.012833507, 0.013210669, 0.013587831, 0.013964993, 0.014342155, 0.014719316, 0.01519292, 0.015666523, 0.016140126, 0.01661373, 0.017087333, 0.017560936, 0.01803454, 0.018508143, 0.018981746, 0.019455349],
        "moment": [0.901559514, 34.7931158, 34.7931158, 34.7931158, 34.7931158, 41.7100224, 49.54709, 57.4781521, 65.4476383, 73.4302856, 81.4129197, 89.3880393, 97.3509562, 105.298457, 113.228173, 121.138216, 129.026963, 136.892962, 144.734849, 152.551277, 160.340899, 168.10235, 175.834201, 183.534969, 191.203066, 198.836833, 206.43447, 213.994063, 221.51354, 228.990662, 236.422999, 243.807903, 251.142482, 258.423566, 265.647656, 272.810892, 279.908987, 286.937169, 293.89008, 300.761699, 309.264704, 317.613022, 325.787976, 333.767034, 341.522621, 349.020412, 356.216809, 363.055063, 369.459078, 375.322824],
    },
    "ELASTIC_ELASTIC": {
        "kappa": [0.00001, 0.001403591, 0.002797182, 0.004190773, 0.005584363, 0.006977954, 0.008371545, 0.009765136, 0.011158727, 0.012552318, 0.013945909, 0.0153395, 0.01673309, 0.018126681, 0.019520272, 0.020913863, 0.022307454, 0.023701045, 0.025094636, 0.026488226, 0.027881817, 0.029275408, 0.030668999, 0.03206259, 0.033456181, 0.034849772, 0.036243362, 0.037636953, 0.039030544, 0.040424135, 0.041817726, 0.043211317, 0.044604908, 0.045998498, 0.047392089, 0.04878568, 0.050179271, 0.051572862, 0.052966453, 0.054360044],
        "moment": [0.878937604, 123.366971, 245.855007, 368.343041, 490.831075, 613.319108, 735.807142, 858.295178, 980.783212, 1103.27125, 1225.75928, 1348.24731, 1470.73535, 1593.22338, 1715.71142, 1838.19945, 1960.68748, 2083.17552, 2205.66355, 2328.15159, 2450.63962, 2573.12765, 2695.61569, 2818.10372, 2940.59176, 3063.07979, 3185.56782, 3308.05586, 3430.54389, 3553.03193, 3675.51996, 3798.008, 3920.49603, 4042.98406, 4165.4721, 4287.96013, 4410.44817, 4532.9362, 4655.42424, 4777.91227],
    },
    "FACTOR_METHOD": {
        "kappa": [2.44841e-06, 9.47427e-05, 0.000187037, 0.000279331, 0.000371627, 0.000463921, 0.001501076, 0.001987468, 0.002445876, 0.002885904, 0.003313299, 0.003731588, 0.004143074, 0.004549282, 0.004951251, 0.005349806, 0.005745613, 0.006139193, 0.006530938, 0.006921123, 0.00730996, 0.007697631, 0.008084295, 0.008469127, 0.008854177, 0.009238562, 0.009622349, 0.010005603, 0.010388379, 0.01077073, 0.011152698, 0.011534313, 0.011915605, 0.012296603, 0.012677332, 0.013057812, 0.013438057, 0.013818082, 0.014197902, 0.014577532, 0.019314732],
        "moment": [0.2152, 8.3273, 16.4394, 24.5515, 32.6637, 40.7758, 48.8879, 56.9880, 65.0496, 73.0783, 81.0860, 89.0796, 97.0633, 105.0336, 112.9780, 120.8910, 128.7748, 136.6354, 144.4772, 152.2971, 160.0880, 167.8460, 175.5697, 183.2616, 190.9249, 198.5552, 206.1477, 213.6998, 221.2100, 228.6783, 236.1032, 243.4797, 250.8041, 258.0740, 265.2880, 272.4417, 279.5279, 286.5416, 293.4790, 300.3370, 374.3411],
    },
}

deflection_setup = {
    'x_positions': [0, 0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1375, 0.15, 0.1625,
                    0.175, 0.1875, 0.2, 0.2125, 0.225, 0.2375, 0.25, 0.2625, 0.275, 0.2875, 0.3, 0.3125, 0.325, 0.3375,
                    0.35, 0.3625, 0.375, 0.3875, 0.4, 0.4125, 0.425, 0.4375, 0.45, 0.4625, 0.475, 0.4875, 0.5
                    ],
    'M_qp': [0, 2.842993213, 5.614011914, 8.313056104, 10.94012578, 13.49522095, 15.9783416, 18.38948774, 20.72865938,
               22.99585649, 25.1910791, 27.3143272, 29.36560078, 31.34489985, 33.25222441, 35.08757446, 36.85095,
               38.54235103, 40.16177754, 41.70922954, 43.18470703, 44.58821001, 45.91973848, 47.17929243, 48.36687188,
               49.48247681, 50.52610723, 51.49776313, 52.39744453, 53.22515142, 53.98088379, 54.66464165, 55.276425,
               55.81623384, 56.28406816, 56.67992798, 57.00381328, 57.25572407, 57.43566035, 57.54362212, 57.57960938
             ],
    'M_rare': [0.0000, 3.7275, 7.3607,10.8995,14.3439,17.6940,20.9497,24.1110,27.1779,30.1505,33.0288,35.8126,38.5021,
               41.0972,43.5980,46.0043,48.3163,50.5340,52.6573,54.6862,56.6207,58.4609,60.2067,61.8581,63.4152,64.8779,
               66.2462,67.5202,68.6998,69.7850,70.7759,71.6724,72.4745,73.1823,73.7957,74.3147,74.7393,75.0696,75.3056,
               75.4471,75.4943
               ],
    'M_cr': [43.2804, 43.4317, 43.5791, 43.7227, 43.8624, 43.9984, 44.1305, 44.2588, 44.3832, 44.5038, 44.6206, 44.7336,
             44.8427, 44.9480, 45.0495, 45.1471, 45.2409, 45.3309, 45.4171, 45.4994, 45.5779, 45.6525, 45.7234, 45.7904,
             45.8536, 45.9129, 45.9684, 46.0201, 46.0680, 46.1120, 46.1522, 46.1886, 46.2212, 46.2499, 46.2748, 46.2958,
             46.3131, 46.3265, 46.3360, 46.3418, 46.3437
             ],
}

kappa_x = {
    'NONE_PARABOLIC': [0.0, 0.000241153, 0.00045953, 0.000657357, 0.000837296, 0.001001506, 0.001151391, 0.001288318, 0.001413413, 0.001528008, 0.001633087, 0.00172962, 0.001818293, 0.001899757, 0.001974633, 0.002043448, 0.002106683, 0.002164839, 0.002218316, 0.002267474, 0.002312638, 0.002354102, 0.002392218, 0.002427135, 0.002459064, 0.002488201, 0.002514724, 0.002538795, 0.002560557, 0.002580141, 0.002597661, 0.002613221, 0.002626911, 0.002638811, 0.00264899, 0.002657514, 0.002664461, 0.002669823, 0.002673632, 0.002675909, 0.002676667],
    'FCTM_PARABOLIC': [0.0, 3.3075e-05, 6.5218e-05, 9.6396e-05, 0.000126617, 0.00015589, 0.000184223, 0.000211624, 0.000238103, 0.000263666, 0.000288323, 0.000312082, 0.00033495, 0.000356935, 0.000378046, 0.000398289, 0.001689377, 0.001826127, 0.001943748, 0.002041748, 0.002124664, 0.002197247, 0.002260961, 0.002317008, 0.002369677, 0.002417274, 0.002458048, 0.002492948, 0.002522776, 0.002548213, 0.002569838, 0.002588142, 0.002603541, 0.002616386, 0.002626972, 0.002635542, 0.002642296, 0.002647392, 0.002650948, 0.002653034, 0.002653726],
    'TENSTIFF_PARABOLIC': [0.0, 3.3089e-05, 6.5245e-05, 9.6435e-05, 0.000126668, 0.000155953, 0.000184297, 0.00021171, 0.000238199, 0.000263773, 0.00028844, 0.000312208, 0.000335085, 0.00035708, 0.000378199, 0.000398451, 0.000425233, 0.000457176, 0.000486913, 0.000514574, 0.000540278, 0.000564134, 0.000586242, 0.000606695, 0.000625577, 0.000642965, 0.000658929, 0.000673534, 0.000686839, 0.000698896, 0.000709752, 0.000719452, 0.000728032, 0.000735526, 0.000741963, 0.000747369, 0.000751763, 0.000755164, 0.000757583, 0.000759487, 0.000760957],
    'ELASTIC_ELASTIC': [0.0, 2.3938e-05, 5.6988e-05, 8.9123e-05, 0.000120343, 0.000150647, 0.000180033, 0.000208501, 0.000236051, 0.000262682, 0.000288393, 0.000313184, 0.000337057, 0.00036001, 0.000382046, 0.000403164, 0.000423368, 0.000442659, 0.00046104, 0.000478514, 0.000495086, 0.000510761, 0.000525544, 0.000539442, 0.000552462, 0.000564613, 0.000575904, 0.000586344, 0.000595944, 0.000604717, 0.000612672, 0.000619822, 0.000626179, 0.000631755, 0.000636561, 0.000640608, 0.000643905, 0.00064646, 0.00064828, 0.00064937, 0.000655104],
    'Factor-Method': [0.0, 3.3877e-05, 6.6838e-05, 9.888e-05, 0.000130004, 0.000160207, 0.00018949, 0.00021785, 0.000245288, 0.000271803, 0.000297395, 0.000322063, 0.000345808, 0.00036863, 0.00039053, 0.001258033, 0.001372765, 0.001475571, 0.001568002, 0.001651325, 0.001726584, 0.001794654, 0.00185632, 0.001912166, 0.001962724, 0.002008458, 0.002049769, 0.002087003, 0.002120465, 0.002150418, 0.002177091, 0.002200683, 0.002221367, 0.002239293, 0.002254586, 0.002267359, 0.002277725, 0.002285716, 0.002291385, 0.002294772, 0.002295898],
}

EI_x = {
    'x_positions': [0, 0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1375, 0.15, 0.1625, 0.175, 0.1875, 0.2, 0.2125, 0.225, 0.2375, 0.25, 0.2625, 0.275, 0.2875, 0.3, 0.3125, 0.325, 0.3375, 0.35, 0.3625, 0.375, 0.3875, 0.4, 0.4125, 0.425, 0.4375, 0.45, 0.4625, 0.475, 0.4875, 0.5],
    'NONE_PARABOLIC': [11789, 11789, 12217, 12646, 13066, 13475, 13877, 14274, 14666, 15050, 15425, 15792, 16150, 16499, 16840, 17171, 17492, 17804, 18105, 18395, 18673, 18941, 19195, 19438, 19669, 19887, 20092, 20284, 20463, 20629, 20781, 20918, 21042, 21152, 21247, 21328, 21394, 21446, 21482, 21504, 21512],
    'FCTM_PARABOLIC': [85955, 85955, 86080, 86239, 86403, 86569, 86734, 86897, 87058, 87216, 87371, 87523, 87672, 87817, 87958, 88096, 21813, 21106, 20662, 20428, 20325, 20293, 20310, 20362, 20411, 20470, 20555, 20657, 20770, 20887, 21006, 21121, 21231, 21333, 21425, 21506, 21574, 21627, 21666, 21690, 21698],
    'TENSTIFF_PARABOLIC': [85919, 85919, 86045, 86204, 86368, 86534, 86699, 86862, 87022, 87181, 87336, 87488, 87636, 87781, 87923, 88060, 86661, 84305, 82482, 81056, 79931, 79038, 78329, 77764, 77316, 76960, 76679, 76459, 76288, 76156, 76056, 75981, 75926, 75886, 75858, 75839, 75827, 75819, 75814, 75766, 75667],
    'ELASTIC_ELASTIC': [118763, 118763, 98512, 93276, 90908, 89582, 88752, 88198, 87814, 87543, 87350, 87215, 87124, 87067, 87037, 87030, 87042, 87070, 87111, 87164, 87227, 87298, 87376, 87459, 87548, 87640, 87734, 87829, 87923, 88017, 88107, 88194, 88276, 88351, 88419, 88478, 88528, 88568, 88597, 88615, 87894],
    'Factor-Method': [83911, 83911, 83986, 84063, 84144, 84228, 84315, 84405, 84500, 84597, 84698, 84803, 84912, 85024, 85140, 27886, 26839, 26112, 25602, 25243, 24994, 24824, 24714, 24647, 24614, 24606, 24616, 24639, 24672, 24711, 24754, 24797, 24840, 24880, 24917, 24950, 24978, 25001, 25017, 25027, 25030],
}

deflection_mm = {
    'NONE_PARABOLIC': [13.66],
    'FCTM_PARABOLIC': [12.15],
    'TENSTIFF_PARABOLIC': [3.52],
    'ELASTIC_ELASTIC': [3.11],
    'Factor-Method': [10.44],
}

# Optional wrapper preserving the original table titles as string keys.
data = {
    "kappa(x)": kappa_x,
    "EI (x)": EI_x,
    "Deflection [mm]": deflection_mm,
}

# Helper Function
def dict_line_to_plot_line(
    data_dict: dict,
    line_key: str,
    *,
    name: str | None = None,
    color=None,
    linestyle: str = "solid",
) -> PlotLine:
    """
    Convert one y-series from a table-style dict into a PlotLine.

    x-values are taken from data_dict["x_positions"].
    y-values are taken from data_dict[line_key].
    """
    x_values = data_dict["x_positions"]
    y_values = data_dict[line_key]

    if len(x_values) != len(y_values):
        raise ValueError(
            f"Length mismatch for {line_key!r}: "
            f"{len(x_values)} x-values but {len(y_values)} y-values."
        )

    return PlotLine(
        x_values,
        y_values,
        name=name or line_key,
        color=color,
        linestyle=linestyle,
    )

# ── kappa(x) lines ────────────────────────────────────────────────────────────

kappa_line_none_parabolic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["NONE_PARABOLIC"],
    name="NONE_PARABOLIC",
    color=TU_COLORS["BLUE"],
    linestyle="solid",
)

kappa_line_fctm_parabolic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["FCTM_PARABOLIC"],
    name="FCTM_PARABOLIC",
    color=TU_COLORS["GREEN"],
    linestyle="solid",
)

kappa_line_tenstiff_parabolic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["TENSTIFF_PARABOLIC"],
    name="TENSTIFF_PARABOLIC",
    color=TU_COLORS["RED"],
    linestyle="solid",
)

kappa_line_elastic_elastic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["ELASTIC_ELASTIC"],
    name="ELASTIC_ELASTIC",
    color=TU_COLORS["VIOLET"],
    linestyle="solid",
)

kappa_line_factor_method = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["Factor-Method"],
    name="Factor-Method",
    color=TU_COLORS["ORANGE"],
    linestyle="solid",
)

kappa_lines = [
    kappa_line_none_parabolic,
    kappa_line_fctm_parabolic,
    kappa_line_tenstiff_parabolic,
    kappa_line_elastic_elastic,
    kappa_line_factor_method,
]

# ── EI(x) lines ───────────────────────────────────────────────────────────────

ei_line_none_parabolic = PlotLine(
    EI_x["x_positions"],
    EI_x["NONE_PARABOLIC"],
    name="NONE_PARABOLIC",
    color=TU_COLORS["BLUE"],
    linestyle="solid",
)

ei_line_fctm_parabolic = PlotLine(
    EI_x["x_positions"],
    EI_x["FCTM_PARABOLIC"],
    name="FCTM_PARABOLIC",
    color=TU_COLORS["GREEN"],
    linestyle="solid",
)

ei_line_tenstiff_parabolic = PlotLine(
    EI_x["x_positions"],
    EI_x["TENSTIFF_PARABOLIC"],
    name="TENSTIFF_PARABOLIC",
    color=TU_COLORS["RED"],
    linestyle="solid",
)

ei_line_elastic_elastic = PlotLine(
    EI_x["x_positions"],
    EI_x["ELASTIC_ELASTIC"],
    name="ELASTIC_ELASTIC",
    color=TU_COLORS["VIOLET"],
    linestyle="solid",
)

ei_line_factor_method = PlotLine(
    EI_x["x_positions"],
    EI_x["Factor-Method"],
    name="Factor-Method",
    color=TU_COLORS["ORANGE"],
    linestyle="solid",
)

ei_lines = [
    ei_line_none_parabolic,
    ei_line_fctm_parabolic,
    ei_line_tenstiff_parabolic,
    ei_line_elastic_elastic,
    ei_line_factor_method,
]

# Helper Function
def parabolic_deflection_values(x_positions: list[float], defl: float) -> list[float]:
    """
    Return parabolic deflection values for the given x-positions.
    """
    if not x_positions:
        return []

    x_0 = x_positions[0]
    x_end = x_positions[-1]

    if x_end == x_0:
        raise ValueError("x_positions must contain at least two different x-values.")

    L = x_end - x_0

    values = []
    for x in x_positions:
        t = (x - x_0) / L
        w = defl * (2 * t - t**2)
        values.append(w)

    return values

# ── Deflection lines ──────────────────────────────────────────────────────────

deflection_line_none_parabolic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["NONE_PARABOLIC"][0],
    ),
    name="NONE_PARABOLIC",
    color=TU_COLORS["BLUE"],
    linestyle="solid",
)

deflection_line_fctm_parabolic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["FCTM_PARABOLIC"][0],
    ),
    name="FCTM_PARABOLIC",
    color=TU_COLORS["GREEN"],
    linestyle="solid",
)

deflection_line_tenstiff_parabolic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["TENSTIFF_PARABOLIC"][0],
    ),
    name="TENSTIFF_PARABOLIC",
    color=TU_COLORS["RED"],
    linestyle="solid",
)

deflection_line_elastic_elastic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["ELASTIC_ELASTIC"][0],
    ),
    name="ELASTIC_ELASTIC",
    color=TU_COLORS["VIOLET"],
    linestyle="solid",
)

deflection_line_factor_method = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["Factor-Method"][0],
    ),
    name="Factor-Method",
    color=TU_COLORS["ORANGE"],
    linestyle="solid",
)

deflection_lines = [
    deflection_line_none_parabolic,
    deflection_line_fctm_parabolic,
    deflection_line_tenstiff_parabolic,
    deflection_line_elastic_elastic,
    deflection_line_factor_method,
]

# ── Moment line ──────────────────────────────────────────────────────────

m_qp_line = PlotLine(
    deflection_setup["x_positions"],
    deflection_setup["M_qp"],
    name="M_qp",
    color=TU_COLORS["BLACK"],
    linestyle="solid",
)

m_rare_line = PlotLine(
    deflection_setup["x_positions"],
    deflection_setup["M_rare"],
    name="M_rare",
    color=TU_COLORS["BLACK"],
    linestyle="--",
)

m_cr_line = PlotLine(
    deflection_setup["x_positions"],
    deflection_setup["M_cr"],
    name="M_cr",
    color=TU_COLORS["BLACK"],
    linestyle="-.",
)

moment_lines = [
    m_qp_line,
    m_rare_line,
    m_cr_line,
]

# ── M-κ lines: support (x = 0) ────────────────────────────────────────────────

m_kappa_support_line_none_parabolic = PlotLine(m_kappa_c1_3_support["NONE_PARABOLIC"]["moment"], m_kappa_c1_3_support["NONE_PARABOLIC"]["kappa"], name="NONE_PARABOLIC", color=TU_COLORS["BLUE"], linestyle="solid")
m_kappa_support_line_fctm_parabolic = PlotLine(m_kappa_c1_3_support["FCTM_PARABOLIC"]["moment"], m_kappa_c1_3_support["FCTM_PARABOLIC"]["kappa"], name="FCTM_PARABOLIC", color=TU_COLORS["GREEN"], linestyle="solid")
m_kappa_support_line_tenstiff_parabolic = PlotLine(m_kappa_c1_3_support["TENSTIFF_PARABOLIC"]["moment"], m_kappa_c1_3_support["TENSTIFF_PARABOLIC"]["kappa"], name="TENSTIFF_PARABOLIC", color=TU_COLORS["RED"], linestyle="solid")
m_kappa_support_line_elastic_elastic = PlotLine(m_kappa_c1_3_support["ELASTIC_ELASTIC"]["moment"], m_kappa_c1_3_support["ELASTIC_ELASTIC"]["kappa"], name="ELASTIC_ELASTIC", color=TU_COLORS["VIOLET"], linestyle="solid")
m_kappa_support_line_factor_method = PlotLine(m_kappa_c1_3_support["FACTOR_METHOD"]["moment"], m_kappa_c1_3_support["FACTOR_METHOD"]["kappa"], name="Factor-Method", color=TU_COLORS["ORANGE"], linestyle="solid")

m_kappa_support_lines = [
    m_kappa_support_line_none_parabolic,
    m_kappa_support_line_fctm_parabolic,
    m_kappa_support_line_tenstiff_parabolic,
    m_kappa_support_line_elastic_elastic,
    m_kappa_support_line_factor_method,
]


# ── M-κ lines: midspan (x = 0.5) ──────────────────────────────────────────────

m_kappa_midspan_line_none_parabolic = PlotLine(m_kappa_c1_3_midspan["NONE_PARABOLIC"]["moment"], m_kappa_c1_3_midspan["NONE_PARABOLIC"]["kappa"], name="NONE_PARABOLIC", color=TU_COLORS["BLUE"], linestyle="solid")
m_kappa_midspan_line_fctm_parabolic = PlotLine(m_kappa_c1_3_midspan["FCTM_PARABOLIC"]["moment"], m_kappa_c1_3_midspan["FCTM_PARABOLIC"]["kappa"], name="FCTM_PARABOLIC", color=TU_COLORS["GREEN"], linestyle="solid")
m_kappa_midspan_line_tenstiff_parabolic = PlotLine(m_kappa_c1_3_midspan["TENSTIFF_PARABOLIC"]["moment"], m_kappa_c1_3_midspan["TENSTIFF_PARABOLIC"]["kappa"], name="TENSTIFF_PARABOLIC", color=TU_COLORS["RED"], linestyle="solid")
m_kappa_midspan_line_elastic_elastic = PlotLine(m_kappa_c1_3_midspan["ELASTIC_ELASTIC"]["moment"], m_kappa_c1_3_midspan["ELASTIC_ELASTIC"]["kappa"], name="ELASTIC_ELASTIC", color=TU_COLORS["VIOLET"], linestyle="solid")
m_kappa_midspan_line_factor_method = PlotLine(m_kappa_c1_3_midspan["FACTOR_METHOD"]["moment"], m_kappa_c1_3_midspan["FACTOR_METHOD"]["kappa"], name="Factor-Method", color=TU_COLORS["ORANGE"], linestyle="solid")

m_kappa_midspan_lines = [
    m_kappa_midspan_line_none_parabolic,
    m_kappa_midspan_line_fctm_parabolic,
    m_kappa_midspan_line_tenstiff_parabolic,
    m_kappa_midspan_line_elastic_elastic,
    m_kappa_midspan_line_factor_method,
]

" ── Plots ──────────────────────────────────────────────────────────"
# Moment, Stiffness, Curvature, Deflection
fig, axes = plt.subplots(
    nrows=4,
    ncols=1,
    figsize=(6, 9),
    constrained_layout=True,
)

ax1, ax2, ax3, ax4 = axes

mirror_plot(
    moment_lines,
    ax=ax1,
    xmarker=0.1,
    ymarker=10,
    flip_y_axis=True,
    title="Moments [kNm]",
    show_x_numbers=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 68),
)

mirror_plot(
    ei_lines,
    ax=ax2,
    xmarker=0.1,
    ymarker=25000,
    flip_y_axis=True,
    title="Stiffness EI [x10³ N/mm²]",
    show_x_numbers=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 140.3),
    y_scale=1e-3,
)

mirror_plot(
    kappa_lines,
    ax=ax3,
    xmarker=0.1,
    ymarker=0.5e-3,
    flip_y_axis=True,
    title="Curvatures [mm/m]",
    show_x_numbers=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 3.4),
    y_scale=1000,
)

mirror_plot(
    deflection_lines,
    ax=ax4,
    xmarker=0.1,
    ymarker=2.5,
    flip_y_axis=True,
    title="Deflection [mm]",
    show_x_numbers=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 17),
)

handles = []
labels = []

for ax in [ax1, ax2, ax3, ax4]:
    ax_handles, ax_labels = ax.get_legend_handles_labels()

    for handle, label in zip(ax_handles, ax_labels):
        if label == "M_qp":
            continue
        if label not in labels:
            handles.append(handle)
            labels.append(label)

fig.legend(
    handles,
    labels,
    loc="outside lower center",
    ncols=2,
    frameon=False,
)

fig.set_constrained_layout_pads(
    hspace=0.1,
    h_pad=0.05,
)

fig.subplots_adjust(bottom=20)

# M-K-Diagrams

fig_mk_support,      ax_support         = plot_moment_curvature_multiple(m_kappa_support_lines, title="C.1_3 with different constitutive laws", x=0.0, xlim = (0, 0.025), ylim = (0, 390), ymarker=50)
fig_mk_midspan,      ax_midspan         = plot_moment_curvature_multiple(m_kappa_midspan_lines, title="C.1_3 with different constitutive laws", x=0.5, xlim = (0, 0.025), ylim = (0, 390), ymarker=50)
fig_mk_support_zoom, ax_support_zoom    = plot_moment_curvature_multiple(m_kappa_support_lines, title="C.1_3 with different constitutive laws", x=0.0, xlim = (0, 0.005), ylim = (0, 100), ymarker=10)
fig_mk_midspan_zoom, ax_midspan_zoom    = plot_moment_curvature_multiple(m_kappa_midspan_lines, title="C.1_3 with different constitutive laws", x=0.5, xlim = (0, 0.005), ylim = (0, 100), ymarker=10)


# ── Save Figure  ──────────────────────────────────────────────────────────
FIGURES_DIR = Path(__file__).resolve().parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

fig.savefig(os.path.join(FIGURES_DIR,"excel_verification.pdf"), bbox_inches="tight")

fig_mk_support.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_support.pdf"), bbox_inches="tight")
fig_mk_midspan.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_midspan.pdf"), bbox_inches="tight")
fig_mk_support_zoom.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_support_zoom.pdf"), bbox_inches="tight")
fig_mk_midspan_zoom.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_midspan_zoom.pdf"), bbox_inches="tight")

plt.show()