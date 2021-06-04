from flask import Blueprint, Response, request, send_from_directory
import json
from subprocess import Popen, PIPE
from datetime import datetime
import youtube_dl #dummy
import ffmpeg #dummy

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/crop-video', methods = [ 'GET' ] )
	def crop_video( ):
		args = request.args

		current_datetime = datetime.now( )
		current_datetime_str = current_datetime.isoformat( )
		video_tmp_filename = 'out.mp4'
		video_output_filename = 'YTC - {}.mp4'.format( current_datetime_str )		

		has_error = False

		command = "ffmpeg $(youtube-dl -g '{}' | sed 's/^/-ss {} -i /') -t {} -c copy {}".format( args[ 'url' ], args[ 'start_time' ], video_tmp_filename, args[ 'duration' ] )
		process = Popen( command.split( ), stdout = PIPE, stderr = PIPE )
		output, error = process.communicate( )

		has_error = ( process.returncode == 0 )

		if has_error:
			return Response( 'NOK', status = 500 )

		succ_response = send_from_directory( "./", filename = video_tmp_filename, as_attachment = True  )
		succ_response[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )

		command = "rm {}".format( video_tmp_filename )
		process = Popen( command.split( ), stdout = PIPE, stderr = PIPE )
		output, error = process.communicate( )

		has_error = ( process.returncode == 0 )

		if has_error:
			return Response( 'NOK', status = 500 )
		else:
			return succ_response