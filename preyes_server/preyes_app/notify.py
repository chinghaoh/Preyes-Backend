from fcm_django.models import FCMDevice
import environ


def notify(client_id, title, body, data, sound=False):
    root_dir = environ.Path(__file__) - 4
    env = environ.Env()
    env_file = str(root_dir.path('.env'))
    env.read_env(env_file)
    try:
        device = FCMDevice.objects.get(user=client_id)
        result = device.send_message(title=title, body=body, data=data, sound=sound,
                                     api_key=env('FCM_KEY'))
        return result['success'] if result['success'] == 1 else result['failure']

    except Exception as e:
        print(f'An error occurred: {e}')
