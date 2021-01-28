import math

N_node = 99546027
N_link = 9741800114
Accuracy = 1e-12
c  = N_link * 1.0 / N_node #average degree

kout_count_dict = {} #kout_count_dict[kout][0]: p(kout); [1]: average kin of the nodes with kout; [2]: m(kout); [3]: probability to pick the nodes, 1 - t^m(k)
kout_kin_count_dict = {}

def theoretically_solving():
    beta_delta = 1e-5
    beta =  beta_delta
    while beta <= 0.005:
        t = N_solve_t(beta)
        theta = N_solve_theta(t)
        p_gout = calculate_gout(t, theta)
        print beta, p_gout
        beta += beta_delta

def calculate_gout(t, theta): # Eq. (16)
    return sum(kout_kin_count_dict[(kout, kin)] * kout_count_dict[kout][3] * (1 - pow(1 - theta, kin)) for (kout, kin) in kout_kin_count_dict)

def N_solve_theta(t): #Solving the self-consistent equation (15).
    x1 = 1.0
    x2 = 1.0
    delta = 1.0
    while delta > Accuracy:
        x1 = x2
        x2 = get_value_theta(t, x1)
        delta = x1 - x2
        if delta < 0:
            delta *= -1
    return x2

def get_value_theta(t, theta): #Left side self-consistent equation (15).
    temp = sum(kout * kout_kin_count_dict[(kout,kin)] * kout_count_dict[kout][3] * (1 - pow(1-theta,kin)) for (kout,kin) in kout_kin_count_dict)
    return temp / c

def N_solve_t(beta): #Solving the parameter t in Eq.(5), by bisection method.
    leftPoint = 0.0
    leftValue = get_value(leftPoint)
    rightPoint = 1.0
    rightValue = get_value(rightPoint)
    if leftValue <= beta:
        return 0
    if rightValue >= beta:
        return 1
    while rightPoint - leftPoint > Accuracy:
        midPoint = (rightPoint + leftPoint) / 2
        midValue = get_value(midPoint)
        if midValue > beta:
            leftPoint = midPoint
            leftValue = midValue
        else:
            rightPoint = midPoint
            rightValue = midValue
    for kout in kout_count_dict:
        kout_count_dict[kout][3] = 1 - pow(midPoint,kout_count_dict[kout][2])
    return midPoint

def get_value(t): #Left side of Eq.(5).
    return sum(kout_count_dict[kout][0] * (1 - pow(t,kout_count_dict[kout][2])) for kout in kout_count_dict)

def kout2activity(kout):
    if kout < 4.41e6:
        p_kout = 0.087 * pow(kout,0.284)
        return p_kout
    else:
        p_kout = 6.5e4 * pow(kout,-0.6)
        return p_kout

def read_data():
    in_file = open('kout_kin_count.txt', 'r')
    for each_line in in_file:
        each_line = each_line.strip()
        data = each_line.split('\t')
        kout = eval(data[0])
        kin = eval(data[1])
        count = eval(data[2])
        kout_kin_count_dict[(kout, kin)] = count * 1.0 / N_node
        if kout in kout_count_dict:
            kout_count_dict[kout][0] += count
            kout_count_dict[kout][1] += kin * count
        else:
            kout_count_dict[kout] = [1.0 * count, 1.0 * kin * count, kout2activity(kout), 0.0]
    for kout in kout_count_dict:
        kout_count_dict[kout][1] /= kout_count_dict[kout][0]
        kout_count_dict[kout][0] /= N_node
    in_file.close()
    print 'Read degree distribution over.'

if __name__ == "__main__":
    read_data()
    theoretically_solving()