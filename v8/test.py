import multiprocessing as iprocessing
 
def task(task_name):
    print(f'Performing task: {task_name}') 
 
# create and start the processes 
if __name__ == '__main__':
    process1 = iprocessing.Process(target=task, args=('Task 1',)) 
    process2 = iprocessing.Process(target=task, args=('Task 2',)) 
    process1.start() 
    process2.start() 
    
    # wait for the processes to finish 
    process1.join() 
    process2.join() 
    
    print('All tasks completed') 