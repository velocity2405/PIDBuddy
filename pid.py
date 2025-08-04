import time
from scipy.optimize import minimize
import matplotlib.pyplot as plt

global kp,ki,kd,setpoint,time_steps,pv_values,error
kp = 0
ki = 0
kd = 0
setpoint=100
time_steps = []
pv_values = []
error = []

# Tuned Constants:
# kp = 9.99986061718341
# ki = 4.590321282880886e-08
# kd = 2.871824579389954e-06


def pidcontroller(setpoint,pv,kp,ki,kd,previous_error, integral, dt):

    current_error = setpoint - pv
    integral += current_error * dt
    derivative = (current_error - previous_error)/dt
    control = kp * current_error + ki * integral + kd * derivative

    return control, current_error, integral

def properties(ss, time_steps,pv_values):
    ss90 = 0.9 * ss
    ss10 = 0.1 * ss
    ind90 = pv_values.index(pv_values[min(range(len(pv_values)), key = lambda i: abs(pv_values[i]-ss90))])
    ind10 = pv_values.index(pv_values[min(range(len(pv_values)), key = lambda i: abs(pv_values[i]-ss10))])

    t90 = time_steps[ind90]
    t10 = time_steps[ind10]
    risetime = abs(t90-t10)

    pvpeak = max(pv_values)
    po = ((pvpeak - ss)/ss)*100

    return risetime, po

def tuner(kp,ki,kd,insertion,update_values,update_icons):
    def costfunc(pid_params):
        kp,ki,kd = pid_params
        output, time, error = simulation(kp,ki,kd)
        setpoint = 100

        cost = sum(e**2 for e in error)

        overshoot = max(output) - setpoint
        if overshoot>0:
            cost += 100*overshoot

        ss_err = abs(output[-1]-setpoint)
        cost += 50*ss_err

        insertion(f"::> Iteration {iteration['count']}")
        iteration['count']+=1
        update_values(kp,ki,kd)
        return cost
        
    iteration = {'count':1}
    initial_guess = [kp,ki,kd]
    insertion(f"::> Initial Guess: {initial_guess}")

    try:
        res = minimize(costfunc,initial_guess,method='Nelder-Mead',options={"maxiter":300,"disp":True})
    except Exception as e:
        insertion(f"Optimization Stopped: {e}")
    finally:
        kp, ki, kd = res.x
        update_values(kp,ki,kd)
        insertion(f'Optimized Values: [{kp},{ki},{kd}]')
        insertion(f'Controller tuned @ {iteration["count"]} iterations!')
        update_icons()

def plot(display_plot):
    ss = pv_values[-1]
    ss_err = abs(ss-setpoint)
    risetime, po = properties(ss,time_steps,pv_values)
    setpoint_values = [100 for _ in range(len(pv_values))]
    
    print(f'Rise Time: {risetime}')
    print(f'Percentage Overshoot: {po} %' )
    print(f'Steady-State Value: {ss}')
    print(f'Steady State Error: {ss_err}')

    fig = plt.figure(figsize=(12, 6))
    graph = fig.add_subplot(1,1,1)

    graph.plot(time_steps, pv_values, label='Process Variable (PV)')
    graph.plot(time_steps, setpoint_values, label='Setpoint', linestyle='--')

    graph.set_xlabel('Time (s)')
    graph.set_ylabel('Value')
    graph.set_title('Process Variable vs. Setpoint')

    graph.legend()
    graph.grid()
    fig.tight_layout()

    display_plot(fig)

def simulation(kp,ki,kd):

    pv_values.clear()
    time_steps.clear()
    error.clear()

    pv = 0
    previous_error = 0
    integral = 0
    dt = 0.1
   
    for i in range(100):
        control, current_error, integral = pidcontroller(setpoint,pv,kp,ki,kd,previous_error,integral,dt)
        error.append(current_error)
        pv += control * dt
        previous_error = current_error

        time_steps.append(i*dt)
        pv_values.append(pv)
        
        time.sleep(dt)

    return pv_values,time_steps, error


