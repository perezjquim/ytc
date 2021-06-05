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

		print( '> Downloading' )
		dl_command = "youtube-dl --youtube-skip-dash-manifest -g --merge-output-format mp4 {}".format( args[ 'url' ] )
		print( 'COMMAND: {}'.format( dl_command ) )
		dl_process = Popen( dl_command.split( ), stdout = PIPE, stderr = PIPE )
		dl_output, dl_error = dl_process.communicate( )
		print( 'OUTPUT: {}'.format( dl_output ) )
		print( 'ERROR: {}'.format( dl_error ) )
		print( '< Downloading' )

		has_error = ( dl_process.returncode != 0 or dl_error )
		if has_error:
			return Response( 'NOK - Error while downloading!', status = 500 )		

		print( '> Cutting' )
		dl_output = dl_output.decode( 'utf-8' ).rstrip( )
		cut_command = "ffmpeg -i '{}' -ss {} -t {} -c copy {}".format( dl_output, args[ 'start_time' ], args[ 'duration' ], video_tmp_filename )
		print( 'COMMAND: {}'.format( cut_command ) )
		cut_process = Popen( cut_command.split( ), stdout = PIPE, stderr = PIPE )
		cut_output, cut_error = cut_process.communicate( )
		print( 'OUTPUT: {}'.format( cut_output ) )
		print( 'ERROR: {}'.format( cut_error ) )
		print( '< cutting' )		

		has_error = ( cut_process.returncode != 0 or cut_error )

		if has_error:
			return Response( 'NOK - Error while cutting!', status = 500 )

		print( '> preparing request' )	
		succ_response = send_from_directory( video_tmp_directory, filename = video_tmp_filename, as_attachment = True  )
		succ_response[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )
		print( '< preparing request' )			

		print( '> cleaning up' )		
		cl_command = "rm {}".format( video_tmp_filename )
		print( 'COMMAND: {}'.format( cl_command ) )
		cl_process = Popen( cl_command.split( ), stdout = PIPE, stderr = PIPE )
		cl_output, cl_error = cl_process.communicate( )
		print( cl_output )
		print( 'OUTPUT: {}'.format( cl_output ) )
		print( 'ERROR: {}'.format( cl_error ) )
		print( '< cleaning up' )		

		has_error = ( cl_process.returncode != 0 or cl_error )

		if has_error:
			return Response( 'NOK - Error while cleaning up!', status = 500 )
		else:
			return succ_response