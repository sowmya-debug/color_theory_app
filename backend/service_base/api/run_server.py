import os
import sys
import time
from aiohttp import web
import aiohttp_cors
import pandas as pd
from color_theory_app_backend_libs import utils
from color_name.endpoints import EndPoints

# end-pount settings
PORT = 4500
CONTENT_TYPE = 'applicaiton/json'

# dir settings
PATH = os.path.dirname(os.path.abspath(__file__))
PATH_log = os.path.join(PATH, 'logs')

# dir for model
DIR_data = os.path.join(os.path.dirname(PATH), 'api/color_name/data')
DATA = 'colors.csv'

PATH_data = os.path.join(DIR_data, DATA)

if not os.path.isfile(PATH_data):
    print(f'No data found in in {PATH_data}')
    sys.exit(1)

try:
    dat = pd.read_csv(PATH_data)

except Exception as e:
    print(f"Cannot read {PATH_data}. Error: {e}")
    sys.exit(1)

if __name__ == '__main__':

    path_log = os.path.join(PATH_log, 'base_api_{}.log'.format(
        time.strftime('%Y%m%d', time.localtime())))
    logger = utils.get_logger(path_log)

    # parse args
    argumets = utils.get_args()
    port = argumets.port

    logger.info(f"Launch API throuh port {port}")

    # get endpoints
    endpoint = EndPoints(logger=logger, data=dat, content_type=CONTENT_TYPE)

    app = web.Application()

    app.router.add_get("/name/rgb", endpoint.get_color_name_rgb)
    app.router.add_get("/name/hex", endpoint.get_color_name_hex)

    # make CORS
    cors_default_opts = aiohttp_cors.ResourceOptions(allow_credentials=True,
                                                     expose_headers="*",
                                                     allow_headers="*",
                                                     allow_methods=["GET"])

    cors = aiohttp_cors.setup(app, defaults={
        "*": cors_default_opts
    })

    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, port=port, reuse_port=True)