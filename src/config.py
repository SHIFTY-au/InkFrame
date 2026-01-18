import yaml

def load_config(file_path):
    config = yaml.safe_load(open(file_path, 'r'))
    return config

if __name__ == "__main__":
    config = load_config('config/app.yaml')
    print(config)