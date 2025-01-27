from precise.skatertools.data.equityhistorical import get_random_dense_log_price_diff
import traceback
import os
from uuid import uuid4
import json
from pprint import pprint
from precise.whereami import TESTSERROR
import pathlib


def manager_test_run(mgr,n_obs=50,n_dim=7):
    """
       Test manager and log an error file as needed
    """
    df = get_random_dense_log_price_diff(k=1, n_obs=n_obs, n_dim=n_dim)
    xs = df.values

    try:
        s = {}
        for y in xs[:n_obs - 5]:
            w, s = mgr(y=y, s=s, e=-1)

        for y in xs[-5:]:
            w, s = mgr(y=y, s=s, e=1)
    except Exception as e:
        error_data = {'traceback':traceback.format_exc(),
         'exception':str(e),
         'manager':mgr.__name__}
        manager_error_dir = os.path.join(TESTSERROR,'managers')
        pathlib.Path(manager_error_dir).mkdir(parents=True, exist_ok=True)
        error_file = os.path.join(manager_error_dir,mgr.__name__+'_'+str(uuid4())+'.json')
        pprint(error_data)
        with open(error_file, 'wt') as fh:
            json.dump(error_data,fh)


