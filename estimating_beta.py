import MySQLdb
import numpy as np

MAX_ID = 99546027
n_news = 253

def read_cascade_size():
    cascade_size_y = {}
    in_file = open('cascade_size.txt', 'r')
    t_id = 1
    for each_line in in_file:
        each_line = each_line.strip()
        each_line = each_line.split('\t')
        cascade_size = eval(each_line[1])
        cascade_size_y[t_id] = cascade_size
        t_id += 1
    return cascade_size_y

def estimating_beta():
    cascade_size_y = read_cascade_size()
    conn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='******', db='weibo_100m')
        # Please fill in the passwd, and the input of the function may be altered based on your database connection.
    cur = conn.cursor()
    for t_id in range(1, n_news+1):
        cascade_size_x = 0
        in_file = open('tracks/T%d.txt'%t_id, 'r')
        rec_or_not = np.array( [False] * (MAX_ID+1) ) # Whether each node receive the information. rec_or_not[0] is not used.
        for each_line in in_file:
            cascade_size_x += 1
            each_line = each_line.strip()
            retweet_user = eval(each_line) # The retweeting user (or post user) who is handle now.
            sql_cmd = "select fans from fan_table where id = %d" % retweet_user
            cur.execute(sql_cmd)
            results = cur.fetchall()
            results = results[0][0]
            if results != '[]': # Follower set is not empty.
                followers = results.split(',')  # The follower list of the retweeting user.
                k_out = len(followers)
                followers[0] = followers[0].strip('[')
                followers[k_out-1] = followers[k_out-1].strip(']')
                for k_now in range(k_out):
                    follower_now = eval(followers[k_now])
                    rec_or_not[follower_now] = True
        rec_nodes_num = sum(rec_or_not)
        p_gout = 1.0*cascade_size_y[t_id]/MAX_ID
        beta = 1.0*cascade_size_x/rec_nodes_num
        print beta, p_gout

if __name__ == "__main__":
    estimating_beta()