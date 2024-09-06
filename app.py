from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import geopandas as gpd
import os
import zipfile

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
        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Read the CSV and convert to GeoDataFrame
        data = pd.read_csv(filepath)
        gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['X1'], data['Y1']))
        
        # Define the output shapefile path (without extension)
        output_base = os.path.join(app.config['OUTPUT_FOLDER'], file.filename.replace('.csv', ''))
        
        # Write the shapefile components (.shp, .shx, .dbf, .cpg)
        gdf.to_file(output_base + '.shp')
        
        # Create a .zip file with all the necessary shapefile components
        zip_path = output_base + '.zip'
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for ext in ['shp', 'shx', 'dbf', 'cpg']:
                zipf.write(output_base + f'.{ext}', arcname=file.filename.replace('.csv', f'.{ext}'))
        
        # Send the .zip file as the downloadable attachment
        return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
