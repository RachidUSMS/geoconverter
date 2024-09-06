from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import geopandas as gpd
import os
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Read the CSV and convert to SHP
        data = pd.read_csv(filepath)
        gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['X1'], data['Y1']))
        
        output_filename = file.filename.replace('.csv', '')
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        os.makedirs(output_folder, exist_ok=True)
        
        # Save the shapefile (generates .shp, .shx, .dbf, and .cpg files)
        gdf.to_file(os.path.join(output_folder, output_filename + '.shp'))
        
        # Zip the files
        output_zip = os.path.join(app.config['OUTPUT_FOLDER'], output_filename + '.zip')
        shutil.make_archive(output_filename, 'zip', output_folder)

        # Send the zip file as the response
        return send_file(output_zip, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
