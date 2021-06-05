from flask import Blueprint, Response, request, send_from_directory
import json
from subprocess import Popen, PIPE
from datetime import datetime
import youtube_dl #dummy
from urllib.parse import unquote

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
		dl_command = " youtube-dl --force-ipv4 -g --merge-output-format mp4 {} ".format( unquote( args[ 'url' ] ) )
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
		yt_stream_urls = dl_output.decode( 'utf-8' ).split( '\n' )
		yt_video_url = unquote( yt_stream_urls[ 0 ] )
		yt_audio_url = unquote( yt_stream_urls[ 1 ] )
		cut_command = "ffmpeg  -y -ss {} -i {} -ss {} -i {} -t {} -c copy -strict -2 {}".format( args[ 'start_time' ], yt_video_url, args[ 'start_time' ], yt_audio_url, args[ 'duration' ], video_tmp_filename )
		print( 'COMMAND: {}'.format( cut_command ) )
		cut_process = Popen( cut_command.split( ), stdout = PIPE, stderr = PIPE )
		cut_output, cut_error = cut_process.communicate( )
		print( 'OUTPUT: {}'.format( cut_output ) )
		print( 'ERROR: {}'.format( cut_error ) )
		print( '< cutting' )		

		#has_error = ( cut_process.returncode != 0 or cut_error )

		#if has_error:
		#	return Response( 'NOK - Error while cutting!', status = 500 )

		print( '> preparing request' )	
		succ_response = send_from_directory( video_tmp_directory, filename = video_tmp_filename, as_attachment = True  )
		succ_response.headers[ 'Content-Disposition' ] = "attachment; filename={};".format( video_output_filename )
		print( '< preparing request' )			

		return succ_response