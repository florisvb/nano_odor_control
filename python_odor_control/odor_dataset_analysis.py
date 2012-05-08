import sys
sys.path.append('/home/caveman/src/floris_functions')
import floris_plot_lib as fpl

import odor_dataset as od
import numpy as np
import matplotlib.pyplot as plt




'''
class OdorTrial(object):
    def __init__(self, position, time, odortrace, odor_on_index, voltage, resistance, gain=1):
        self.position = position
        self.time = time
        self.odortrace = odortrace
        self.odor_on_index = odor_on_index
        self.voltage = voltage
        self.resistance = resistance
        self.gain = gain
        
class InterpolatedTrial(object):
    def __init__(self, time, odortrace, odor_value):
        self.time = time
        self.odortrace = odortrace
        self.odor_value = odor_value
        
class OdorExperiment(object):
    def __init__(self, pulse, odor_type):
        self.trials = {}
        self.pulse = pulse
        self.odor_type = odor_type
'''
def fix_odor_trace(dataset):
    for exp_key, experiment in dataset.experiments.items():
        for trial_key, trial in experiment.trials.items():
            try:
                trial.odor_trace = trial.odortrace
            except:
                pass
            try:
                del(trial.odortrace)
            except:
                pass
                
def calc_odor_value(trial):
    voltage_divider_gain = 1-((102 - trial.resistance) / 101)
    trial.odor_value = (trial.voltage/trial.gain)/voltage_divider_gain

def interpolate_trial(trial, frequency=500.):
    calc_odor_value(trial)
    new_time_sec = np.arange(-1, 10, 1./float(frequency))
    new_time_micros = new_time_sec*1e6
    new_odor_value = np.interp(new_time_micros, trial.time, trial.odor_value)
    new_odor_trace = np.interp(new_time_micros, trial.time, trial.odor_trace)
    
    # remove dc offset in odor trace:
    new_odor_on_index = np.where(new_odor_trace>0)[0][0]
    mean_no_odor = np.mean(new_odor_value[0:new_odor_on_index])
    new_odor_value -= mean_no_odor
        
    trial.interpolated = od.InterpolatedTrial(new_time_sec, new_odor_trace, new_odor_value, new_odor_on_index)

def calc_mean_for_experiment(experiment):
    
    positions = None
    odor_values = None
    odor_traces = None
    
    for key, trial in experiment.trials.items():
        interpolate_trial(trial)
        if positions is None:
            positions = trial.position
            odor_values = trial.interpolated.odor_value
            odor_traces = trial.interpolated.odor_trace
        else:
            positions = np.vstack((positions, trial.position))
            odor_values = np.vstack((odor_values, trial.interpolated.odor_value))
            odor_traces = np.vstack((odor_traces, trial.interpolated.odor_trace))
        
    # means
    mean_position = np.mean(positions, axis=0)
    mean_odor_value = np.mean(odor_values, axis=0)
    mean_odor_trace = np.mean(odor_traces, axis=0)
    mean_odor_on_index = np.where(mean_odor_trace>0)[0][0]
    
    # std
    std_position = np.std(positions, axis=0)
    std_odor_value = np.std(odor_values, axis=0)
    std_odor_trace = np.std(odor_traces, axis=0)
    std_odor_on_index = np.where(mean_odor_trace>0)[0][0]
    
    base_trial_key = experiment.trials.keys()[0]
    base_trial = experiment.trials[base_trial_key]
    
    # save mean
    mean_trial = od.OdorTrial(mean_position, base_trial.interpolated.time, mean_odor_trace, mean_odor_on_index, None, base_trial.resistance, base_trial.gain)
    mean_trial.odor_value = mean_odor_value
    experiment.mean_trial = mean_trial
    
    # save std
    std_trial = od.OdorTrial(std_position, base_trial.interpolated.time, std_odor_trace, std_odor_on_index, None, base_trial.resistance, base_trial.gain)
    std_trial.odor_value = std_odor_value
    experiment.std_trial = std_trial
    
def calc_means_for_dataset(dataset):
    for exp_key, experiment in dataset.experiments.items():
        calc_mean_for_experiment(experiment)
        
        
def set_zero_pos(dataset, zero_pos):
    for exp_key, exp in dataset.experiments.items():
        for trial_key, trial in exp.trials.items():
            trial.position -= zero_pos
        exp.mean_trial.position -= zero_pos
    
############### PLOTTING #################    
        
def plot_mean_odor_traces(dataset):
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for exp_num in dataset.experiments.keys():

        #exp_num = 2

        exp = dataset.experiments[exp_num]
        
        dc_offset = exp.mean_trial.position[1]
        #print dc_offset
        scale = .0001
        
        print '****'
        print exp.mean_trial.odor_on_index
        print np.mean(exp.mean_trial.odor_value[0:exp.mean_trial.odor_on_index])
        print np.min(exp.mean_trial.odor_value[0:exp.mean_trial.odor_on_index])
        print
        
        ax.plot(exp.mean_trial.time, exp.mean_trial.odor_value*scale + dc_offset, color='black', linewidth=.5)
        
        for trial_key, trial in exp.trials.items():
            ax.plot(trial.interpolated.time, trial.interpolated.odor_value*scale + dc_offset, color='gray', linewidth=.25, zorder=-5)
        
        #ax.fill_between(exp.mean_trial.time, np.log(exp.mean_trial.odor_value-exp.std_trial.odor_value+10)*scale + dc_offset, np.log(exp.mean_trial.odor_value+exp.std_trial.odor_value+10)*scale + dc_offset, color='gray', zorder=-10)

    fpl.adjust_spines(ax, ['left', 'bottom'])
    
    ax.set_xlabel('time, s')
    ax.set_ylabel('distance from source')
    
    fig.savefig('odor_trace_example.pdf', format='pdf')
    













