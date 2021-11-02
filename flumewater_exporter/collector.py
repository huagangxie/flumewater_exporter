import prometheus_client.core


class FlumewaterCollector(object):

    def __init__(self, api):
        self.api = api
        self._prefix = "flumewater_"
        self.api.credentials()
        self.api.userid()
        self._devices = self.api.device_list()
    
    def make_metric(self, _is_counter, _name, _documentation, _value,
                    **_labels):
        if _is_counter:
            cls = prometheus_client.core.CounterMetricFamily
        else:
            cls = prometheus_client.core.GaugeMetricFamily
        label_names = list(_labels.keys())
        metric = cls(
            _name, _documentation or "No Documentation", labels=label_names)
        metric.add_metric([str(_labels[k]) for k in label_names], _value)
        return metric

    def collect(self):
        metrics = []
        # Get Creditial 
        # getUserID 
        # self.api.userid()
        # getDevices 
        for device in self._devices:
            # query last mins and current month's usage, maybe more in the future 
            qdata = self.api.device_query(device, all=False)

            if qdata == None: 
                self.api.credentials()
                self.api.userid()
                self._devices = self.api.device_list()
                logging.debug("Qdata is NULL and re-register the device")
            else :
                cur_month = self.make_metric(
                    True, self._prefix + "month",
                    "current month water usage ",
                    qdata[1], device_id=device) 
                metrics.append(cur_month)

                last_min = self.make_metric(
                    False, self._prefix + "usage",
                    "last one min water usage",
                    qdata[0], device_id=device)

                metrics.append(last_min)

        return metrics
