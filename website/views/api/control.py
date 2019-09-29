from django.http import HttpResponse
from django.db import transaction 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from website.helpers.json_api import reqArgs, jsonResponse, errResponse

from website.models import MagicKey
from website.helpers import util
from time import sleep

import json, datetime, time, re, pytz, uuid, hashlib
import RPi.GPIO as GPIO


@csrf_exempt
@reqArgs()
def request_challenge( request, *args, **kwargs ):
    challenge = util.createHash()
    answer = util.createHash( MagicKey.getMagicKey(), challenge )

    # Set the answer to the hash
    if answer == challenge or answer is None or \
       len(util.xstr(answer)) != 64 or len(util.xstr(challenge)) != 64:
        return errResponse( request, "Invalid" )

    # Store the answer into the cache engine
    cache.set("challenge_response", answer)

    return jsonResponse( request, { 'challenge': challenge })


@csrf_exempt
@reqArgs( post_req=[
              ('challenge_response', str),
          ],
)
def toggle_door( request, challenge_response, *args, **kwargs ):
    # Get the correct, answer, then delete it
    correct = cache.get( "challenge_response" )
    cache.delete( "challenge_response" )

    # Ensure they had the right answer
    if correct != challenge_response or \
       len(util.xstr(correct)) != 64 or len(util.xstr(challenge_response)) != 64:
        return errResponse( request, "Invalid challenge response")

    # Drive the gpio
    pin = 28
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup( pin, GPIO.OUT, initial=0)

    GPIO.output(pin, True)
    sleep(2)
    GPIO.output(pin, False)

    return jsonResponse( request, {})


@csrf_exempt
@reqArgs( post_req=[
              ('challenge_response', str),
          ],
)
def door_status( request, challenge_response, *args, **kwargs ):
    # Get the correct, answer, then delete it
    correct = cache.get( "challenge_response" )
    cache.delete( "challenge_response" )

    # Ensure they had the right answer
    if correct != challenge_response or \
       len(util.xstr(correct)) != 64 or len(util.xstr(challenge_response)) != 64:
        return errResponse( request, "Invalid challenge response")

    # Drive the gpio
    pin = 27
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup( pin, GPIO.IN)

    return jsonResponse( request, {'status': util.xbool(GPIO.input(pin))
                                  })

@csrf_exempt
@reqArgs()
def download_magic_key( request, *args, **kwargs ):
    # Get the correct, answer, then delete it
    result = cache.get( "magic_key" )
    cache.delete( "magic_key" )

    # Ensure they had the right answer
    if result != 'download_key':
        return errResponse( request, "Invalid challenge response")

    return jsonResponse( request, {'magic_key': MagicKey.getMagicKey()
                                   })