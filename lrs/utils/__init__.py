import ast
import json
import urllib
import re
import unicodedata
import math

from urllib.parse import parse_qs, parse_qsl, urlparse, unquote_plus

from datetime import datetime, timezone
from isodate.isodates import parse_date
from isodate.isodatetime import parse_datetime
from isodate.isoerror import ISO8601Error
from isodate.isotime import parse_time

from django.conf import settings
from django.utils.timezone import utc

from ..exceptions import ParamError

agent_ifps_can_only_be_one = ['mbox', 'mbox_sha1sum', 'openid', 'account']


# Exception type to accommodate RFC 3339 timestamp validation.
class RFC3339Error(ValueError):
    pass

def validate_timestamp(time_str):
    time_ret = None
    rfc_ret = None

    try:
        time_ret = parse_datetime(time_str)
    except (Exception, ISO8601Error):
        try:
            date_out, time_out = time_str.split(" ")
        except ValueError:
            raise RFC3339Error("Time designators 'T' or ' ' missing. Unable to parse datetime string %r." % time_str)
        else:
            date_temp = parse_date(date_out)
            time_temp = parse_time(time_out)
            time_ret = datetime.combine(date_temp, time_temp)
    
    if time_ret is not None:
        rfc_ret = None
        try:
            rfc_ret = time_ret.replace(tzinfo=utc)
        except ValueError:
            rfc_ret = time_ret
    
    return rfc_ret


def get_agent_ifp(data):
    ifp_sent = [
        a for a in agent_ifps_can_only_be_one if data.get(a, None) is not None]

    ifp = ifp_sent[0]
    ifp_dict = {}

    if not 'account' == ifp:
        ifp_dict[ifp] = data[ifp]
    else:
        if not isinstance(data['account'], dict):
            account = json.loads(data['account'])
        else:
            account = data['account']

        ifp_dict['account_homePage'] = account['homePage']
        ifp_dict['account_name'] = account['name']
    return ifp_dict


def convert_to_datetime_object(timestr):
    try:
        date_object = validate_timestamp(timestr)
    except ValueError as e:
        raise ParamError(
            "There was an error while parsing the date from %s -- Error: %s" % (timestr, str(e)))
    return date_object


def convert_to_datatype(incoming_data):
    data = {}
    # GET data will be non JSON string-have to try literal_eval
    if isinstance(incoming_data, dict) or isinstance(incoming_data, list):
        return incoming_data
    
    # could get weird values that json lib will parse
    # ex: '"this is not json but would not fail"'

    # The move to newer Django and Python3 means that the request body
    # will be passed as bytes and may need decoding here
    # if isinstance(incoming_data, bytes)
    decoded = incoming_data if isinstance(incoming_data, str) else incoming_data.decode("utf-8")
    
    if decoded.startswith('"'):
        decoded = decoded[1:-1]
    try:
        data = json.loads(decoded)
    except Exception:
        try:
            data = ast.literal_eval(decoded)
        except Exception as e:
            raise e
    return data


def convert_post_body_to_dict(incoming_data):
    encoded = True

    decoded = incoming_data if isinstance(incoming_data, str) else incoming_data.decode("utf-8")

    pairs = [s2 for s1 in decoded.split('&') for s2 in s1.split(';')]
    for p in pairs:
        # this is checked for cors requests
        if p.startswith('content='):
            if p == unquote_plus(p):
                encoded = False
            break
    qs = parse_qsl(decoded)
    return dict((k, v) for k, v in qs), encoded


def get_lang(langdict, lang):
    if lang:
        if 'all' in lang:
            return langdict
        else:
            for la in lang:
                if la == "anylanguage":
                    try:
                        return {settings.LANGUAGE_CODE: langdict[settings.LANGUAGE_CODE]}
                    except KeyError:
                        first = next(iter(langdict.items()))
                        return {first[0]: first[1]} 
                # Return where key = lang
                try:
                    return {la: langdict[la]}
                except KeyError:
                    # if the language header does match any exactly, then if it is only a 2 character
                    # header, try matching it against the keys again ('en' would match 'en-US')
                    if not '-' in la:
                        # get all keys from langdict...get all first parts of them..if la is in it, return it
                        for k in list(langdict.keys()):
                            if '-' in k:
                                if la == k.split('-')[0]:
                                    return {la: langdict[k]}                    
                    pass
    first = next(iter(langdict.items()))
    return {first[0]: first[1]}
