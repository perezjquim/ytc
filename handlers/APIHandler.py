from flask import Blueprint, Response, request, send_from_directory
import json
from subprocess import Popen, PIPE
from datetime import datetime
import youtube_dl #dummy

api = Blueprint( "APIHandler", __name__ )

class APIHandler( ):

	def get_blueprint( self ):
		return api	

	@api.route( '/crop-video', methods = [ 'GET' ] )
	def crop_video( ):
		args = request.args

		current_datetime = datetime.now( )
		current_datetime_str = current_datetime.isoformat( )
		video_tmp_directory = './'
		video_tmp_filename = 'out.mp4'
		video_output_filename = 'YTC - {}.mp4'.format( current_datetime_str )		

		has_error = False

		print( '> Downloading and cutting' )
		command = "ffmpeg $(youtube-dl -g '{}' | sed 's/^/-ss {} -i /') -t {} -c copy {}".format( args[ 'url' ], args[ 'start_time' ], args[ 'duration' ], video_tmp_filename )
		print( 'COMMAND: {}'.format( command ) )
		process = Popen( command.split( ), stdout = PIPE, stderr = PIPE )
		output, error = process.communicate( )
		print( 'OUTPUT: {}'.format( output ) )
		print( 'ERROR: {}'.format( error ) )
		print( '< Downloading and cutting' )

		has_error = ( process.returncode == 0 or error )

		if has_error:
			return Response( 'NOK', status = 500 )

		print( '> preparing request' )	
		succ_response = send_from_directory( video_tmp_directory, filename = video_tmp_filename, as_attachment = True  )
		succ_response[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )
		print( '< preparing request' )			

		print( '> cleaning up' )		
		command = "rm {}".format( video_tmp_filename )
		print( 'COMMAND: {}'.format( command ) )
		process = Popen( command.split( ), stdout = PIPE, stderr = PIPE )
		output, error = process.communicate( )
		print( output )
		print( 'OUTPUT: {}'.format( output ) )
		print( 'ERROR: {}'.format( error ) )
		print( '< cleaning up' )		

		has_error = ( process.returncode == 0 or error )

		if has_error:
			return Response( 'NOK', status = 500 )
		else:
			return succ_response