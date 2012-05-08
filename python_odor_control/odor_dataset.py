import pickle

def save(dataset, filename):
    print 'saving dataset to file: ', filename
    fname = (filename)  
    fd = open( fname, mode='w' )
    pickle.dump(dataset, fd)
    fd.close()
    return 1
    
def load(filename):
    fname = (filename)
    fd = open( fname, mode='r')
    print 'loading data... '
    dataset = pickle.load(fd)
    fd.close()
    return dataset

class OdorData(object):
    def __init__(self):
        pass
        
class OdorTrial(object):
    def __init__(self, position, time, odor_trace, odor_on_index, voltage, resistance, gain=1):
        self.position = position
        self.time = time
        self.odor_trace = odor_trace
        self.odor_on_index = odor_on_index
        self.voltage = voltage
        self.resistance = resistance
        self.gain = gain
        
class InterpolatedTrial(object):
    def __init__(self, time, odor_trace, odor_value, odor_on_index):
        self.time = time
        self.odor_trace = odor_trace
        self.odor_value = odor_value
        self.odor_on_index = odor_on_index
        
class OdorExperiment(object):
    def __init__(self, pulse, odor_type):
        self.trials = {}
        self.pulse = pulse
        self.odor_type = odor_type
        
class OdorDataset(object):
    def __init__(self):
        self.experiments = {}
