#!/usr/bin/env python3
# coding=utf-8
import requests
from mpms import MultiProcessesMultiThreads


def worker(no, url):
    print("requesting", no, url)
    r = requests.get(url)
    with open("{}.html".format(no), "wb") as fw:  # 将内容写入文件, 这也是比较耗时的IO操作
        fw.write(r.content)
    return no, r.url, r.status_code, len(r.content), r.elapsed.total_seconds()


def handler(meta, no, url, status_code, length, time):
    # 其中第一个参数 meta 不是由 worker() 传入的, 其他几个跟 worker() 的返回值一一对应
    #    正如字面意思, 它包含了一些在初始化时传入的参数
    #    在本例中, 为了演示, 传入了一个文件对象, 用于写日志
    print("Done:", no, url, status_code, length, time)

    fw = meta["log_file"]
    fw.write("{} {} {} {} {}\n".format(no, url, status_code, length, time))

    meta["total_req_time"] += time  # 统计总共的耗时


def main():
    fw = open("log.txt", "w", encoding="utf-8")

    m = MultiProcessesMultiThreads(
        worker,
        handler,
        processes=5,
        threads_per_process=10,
        meta={"log_file": fw, "total_req_time": 0.0},
    )

    for i in range(1000):  # 请求1000次
        m.put([i, "http://example.com/?q=" + str(i)])

    m.join()
    fw.close()

    return m.meta["total_req_time"]


if __name__ == '__main__':
    from time import time

    start = time()
    total_req_time = main()
    spent_time = time() - start
    print("------- Done --------")
    print("Total request time:", total_req_time)
    print("Real time spent:", spent_time)
    print("You are faster about: {}x".format(round(total_req_time / spent_time, 3)))
