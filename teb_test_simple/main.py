import multiprocessing
import subprocess


api_process = multiprocessing.Process(
    target=subprocess.run,
    kwargs={
        'args': f'py teb_test_simple/web.py',
        'shell': True
    })


bot_process = multiprocessing.Process(
    target=subprocess.run,
    kwargs={
        'args': f'py teb_test_simple/bot.py',
        'shell': True
    })


if __name__ == '__main__':
    api_process.start()
    bot_process.start()