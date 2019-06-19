import os
import sys
import time
import json
from aiohttp import web
import aiohttp_cors
from color_theory_app_backend_libs import utils
from ml_model.endpoints import EndPoints
from ml_model.predictor import Predict


# end-pount settings
PORT = 4500
CONTENT_TYPE = 'applicaiton/json'

# dir settings
PATH = os.path.dirname(os.path.abspath(__file__))
PATH_log = os.path.join(PATH, 'logs')

# secrets - API keys list
PATH_secrets = os.path.join(PATH, 'secrets.json')

# dir for model
DIR_model = os.path.join(os.path.dirname(PATH), 'ml/model')
MODEL = 'model_v1.xgb'

PATH_model = os.path.join(DIR_model, MODEL)

if not os.path.isfile(PATH_model):
    print(f'No model found in in {PATH_model}')
    sys.exit(1)


if __name__ == '__main__':

    path_log = os.path.join(PATH_log, 'ml_api_{}.log'.format(
        time.strftime('%Y%m%d', time.localtime())))
    logger = utils.get_logger(path_log)

    # parse args
    argumets = utils.get_args()
    port = argumets.port

    apikeys = None
    if os.path.isfile(PATH_secrets):
        apikeys = json.load(open(PATH_secrets, 'r'))

    logger.info(f"Launch API throuh port {port}")

    try:
        # get the model
        predictor = Predict(logger=logger, path_model=PATH_model)

        # get endpoints
        endpoint = EndPoints(logger=logger,
                             predictor=predictor,
                             content_type=CONTENT_TYPE,
                             secrets=apikeys)

    except Exception as e:
        logger.error(e)
        print(e)
        sys.exit(1)

    app = web.Application()

    app.router.add_get("/rgb", endpoint.get_color_cat_rgb)
    app.router.add_get("/hex", endpoint.get_color_cat_hex)

    # make CORS
    cors_default_opts = aiohttp_cors.ResourceOptions(allow_credentials=False,
                                                     expose_headers="*",
                                                     allow_headers=("Content-Type", "APIKEY"),
                                                     allow_methods=["GET"])

    cors = aiohttp_cors.setup(app, defaults={
        'color-theory-app.dkisler.com': cors_default_opts
    })

    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, port=port, reuse_port=True)
