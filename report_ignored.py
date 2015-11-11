#!/usr/bin/python3
import praw, pickle
_pickle_filename = "pickle.cache"
def main():
    to_report = pickle.load(open(_pickle_filename, 'rb'))
    for i in range(len(to_report)):
        print("Item {} ; Prediction: {}".format(i, to_report[i][1]))
        print(to_report[i][0].body)

if __name__=="__main__":
    main()
        
