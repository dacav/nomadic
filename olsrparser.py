#!/usr/bin/env python
import re

class OlsrParser(object):
    TOPOLOGY_REGEX=r"^-+ ([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}) -+ TWO-HOP NEIGHBORS.*$"
    def __init__(self, path):
        self.path = path
        self.olsr_log = None

    def __normtstamp(self, tstamp):
        TSTAMP_REGEX=r"([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{6})"
        ttlst = re.findall(TSTAMP_REGEX,tstamp)

        if len(ttlst) == 0: raise ValueError("Non a valid time stamp")
        h, m, s, usec = ttlst[0]
        t = (int(h)*(60**2) + int(m)*60 + int(s)) * 1000 + int(usec[:3])

        return t

    def __parse_neighbors(self):
        normcost = lambda x: float(x) if x != "INFINITE" else 9999999
        host_dict={}
        curr_host = ""
        for line in self.olsr_log:
            line = line.strip()
            #if we got to the end of the section we're done
            if line.startswith("---"): break

            #just ignore the header and blank lines!
            if line.startswith("IP") or line == "": continue

            data = filter(lambda x: x != "", line.split(" "))
            if len(data) > 2:
                #here we go with another dest
                curr_host = data[0]
                host_dict[curr_host] = (data[1], normcost(data[2]))
            else:
                #consider this path for the old dest
                curr_cost = host_dict[curr_host][1]
                new_cost = normcost(data[1])
                if new_cost < curr_cost:
                    host_dict[curr_host] = (data[0], new_cost)

        return host_dict



    def __parse(self, dest):
        time = None
        result = []
        for line in self.olsr_log:
            match_lst = re.findall(self.TOPOLOGY_REGEX, line)

            # Burn lines unti we get to the start of the Neighbor section
            if len(match_lst) == 0: continue

            tstamp = self.__normtstamp(match_lst[0])
            if time == None: time = tstamp
            host_dict = self.__parse_neighbors()

            hop, cost = host_dict.get(dest, ("none", 0))
            result.append(((tstamp - time) / 1000, hop))

        return result

    def parse(self, dest):
        self.olsr_log = open(self.path, "r")
        return self.__parse(dest)
        self.olsr_log.close()


if __name__ == "__main__":
    import sys
    log_file = sys.argv[1]
    destination = sys.argv[2]

    parser = OlsrParser(log_file)
    res = parser.parse(destination)
    print res
