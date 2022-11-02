
############################ Categorized legend
# input: 
# 1.layer to render, 
# 2. string: attribute to use, 
# 3. dictionary for the legend with key=attribute value and entries 
# a) string: label, 
# b) QColor: color, 
# c) float: opacity
# no output
def create_categorized_legend(vlayer,attrib,dict):
    # create categories from mydict
    categories=[] # empty list
    for myvalue, (mylabel,myQcolor, myopacity) in dict.items():
        mysymbol=QgsSymbol.defaultSymbol(vlayer.geometryType())
        mysymbol.setColor(myQcolor)
        mysymbol.setOpacity(myopacity)
        cat=QgsRendererCategory(myvalue, mysymbol, mylabel)
        categories.append(cat)
    # create renderer
    renderer = QgsCategorizedSymbolRenderer(attrib, categories)
    vlayer.setRenderer(renderer)
    # Refresh layer
    vlayer.triggerRepaint()

# input dictionary myvalue: (Qcolor, opacity)
def create_categorized_legend_3_arg(vlayer,attrib,dict):
    # create categories from mydict
    categories=[] # empty list
    for mylabel, (myvalue, myQcolor, myopacity) in dict.items():
        mysymbol=QgsSymbol.defaultSymbol(vlayer.geometryType())
        mysymbol.setColor(myQcolor)
        mysymbol.setOpacity(myopacity)
        cat=QgsRendererCategory(int(myvalue), mysymbol, mylabel)
        categories.append(cat)
    # create renderer
    renderer = QgsCategorizedSymbolRenderer(attrib, categories)
    vlayer.setRenderer(renderer)
    # Refresh layer
    vlayer.triggerRepaint()


# function that creates dictionary from list of values
# requires package random
def create_random_categorized_dict(myListValues,colorMin=0,colorMax=255,opacity=1):
    myDict={} # initialize
    # creates dictionary: one entry per value in myListValues
    for val in myListValues:
        val = str(val) # to be sure it is a string
        myR=random.randint(colorMin,colorMax) 
        myG=random.randint(colorMin,colorMax)
        myB=random.randint(colorMin,colorMax)
        myQColor=QColor(myR,myG,myB)
        # insert a new entry to the dictionary
        myDict.update({val : (val,myQColor,opacity)})
    return myDict

########################################  graduated legend
# creates dictionary for legend;: requires matplotlib
# values is a list of values that have to be represented in the legend
# each legend class corresponds to a interval from 10**i to 10**(i+1)
# the 1st class starts at 0
# mymindigits is the smallest (i+1) that is greater than digits of min(values)
# mymaxdigits is the largest (i+1) that is greater than digits of max(values)
# colomap is the name of a matplotlib colormap with a .colors attribute
# myopacity is a constant opacity value
# output: a dictionary where keys are the class labels
# each dict value is (minClass,maxClass,QColor,myopacity)
def create_graduated_legend_dict(values,colormap,myopacity):
    from matplotlib.cm import get_cmap
    import numpy as np
    mymin=min(values)
    mymindigits=int(np.ceil(np.log10(max(mymin,10))))
    mymax=max(myListValues)
    mymaxdigits=int(np.ceil(np.log10(max(10,mymax))))
    # Creates dictionary for the graduated legend
    myDict={} # initialize
    count=0
    # number of classes
    N=mymaxdigits+1-mymindigits
    # color using colormap defined in the header of the script
    #mycolormap=matplotlib.cm.get_cmap(colormap,N) 
    mycolormap=get_cmap(colormap,N) 
    #mycolors=mycolormap.colors*255 # numpy.ndarray
    for i in range(mymindigits,mymaxdigits+1):
        # determine class minimum and maximum value
        if i==mymindigits: 
            classMin = 0
        else:
            classMin = classMax
        classMax = 10**i
        # label for the class:
        classMinKm2=int(classMin/10**6)
        classMaxKm2=int(classMax/10**6)
        mylabel = 'from {} to {} km2'.format(classMinKm2,classMaxKm2)
        # choose count-th color from mycolors
        #mycolor=mycolors[count]
        # create QColor object
        mycolor=mycolormap(count)
        myQColor=QColor(mycolor[0],mycolor[1],mycolor[2]) #RGB
        # insert a new entry to the dictionary
        myDict.update({mylabel : (classMin,classMax,myQColor,myopacity)})
        count +=1
    return myDict

# junho 2022
def create_unary_graduated_legend_dict(values,colormap,myopacity,decimals):
    from matplotlib.cm import get_cmap
    import numpy as np
    mymin=int(np.floor(min(values)))
    mymax=int(np.ceil(max(values)))
    # Creates dictionary for the graduated legend
    myDict={} # initialize
    count=0
    # number of classes
    N=int(mymax+1-mymin)*10**decimals
    # color using colormap defined in the header of the script
    #mycolormap=matplotlib.cm.get_cmap(colormap,N) 
    mycolormap=get_cmap(colormap,N) 
    #mycolors=mycolormap.colors*255 # numpy.ndarray
    while count<N:
        t=mymin+count*10**(-decimals)
        mylabel = 'day {}'.format(t)
        # create QColor object
        mycolor=[255*x for x in mycolormap(count)]
        myQColor=QColor(mycolor[0],mycolor[1],mycolor[2]) #RGB
        # insert a new entry to the dictionary
        myDict.update({mylabel : (t,t+10**(-decimals),myQColor,myopacity)})
        count +=1
    return myDict


def create_sturges_graduated_legend_dict(values,colormap,myopacity,units):
    from matplotlib.cm import get_cmap
    import numpy as np
    mymin=min(values)
    mymax=max(values)
    # Creates dictionary for the graduated legend
    myDict={} # initialize
    count=0
    N = int(np.ceil(1+np.log2(len(values))))
    breaks=np.linspace(0,mymax,num=N)
    # color using colormap defined in the header of the script
    #mycolormap=matplotlib.cm.get_cmap(colormap,N) 
    mycolormap=get_cmap(colormap,N) 
    mycolors=mycolormap.colors*255 # numpy.ndarray
    for i in range(1,len(breaks)):
        # determine class minimum and maximum value
        if i==1: 
            classMin = 0
        else:
            classMin = classMax
        classMax = breaks[i]
        mylabel = 'from {} to {} {}'.format(round(classMin),round(classMax),units)
        # choose count-th color from mycolors
        mycolor=mycolors[count]
        count +=1
        # create QColor object
        myQColor=QColor(mycolor[0],mycolor[1],mycolor[2]) #RGB
        # insert a new entry to the dictionary
        myDict.update({mylabel : (classMin,classMax,myQColor,myopacity)})
    return myDict

# creates graduated symbology from dictionary with structure as above
# edited junho 2022
def create_graduated_legend(vlayer,att_color,dict,tipo="Circle",att_size=NULL):
    myRangeList=[]
    count=0
    for mylabel, (classMin,classMax, myQColor, myopacity) in dict.items():
        mySymbol = QgsSymbol.defaultSymbol(mylayer.geometryType())
        if tipo=='Circle':
            mySymbol.symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Circle)
        if tipo=='Square':
            mySymbol.symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Square)
        if att_size!=NULL:
            mySymbol.symbolLayer(0).setDataDefinedProperty(QgsSymbolLayer.PropertySize, QgsProperty.fromField(att_size) )
        mySymbol.setColor(myQColor)
        mySymbol.setOpacity(myopacity)
        # new for graduated symbols:
        myRange = QgsRendererRange(classMin, classMax, mySymbol, mylabel)
        myRangeList.append(myRange)
    # define GraduatedSymbol renderer and pass it to mylayer
    renderer = QgsGraduatedSymbolRenderer(att_color, myRangeList)
    vlayer.setRenderer(renderer)
    # Refresh layer
    vlayer.triggerRepaint()

# layer6.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)

############################################  raster legend
# legend for raster 
# type is 'Linear' (interpolated ramp), 'Discrete', 'Exact',...
# inputs: layer and dictionary with label: (color, limite)
def create_raster_ramp_legend(lyr,dict, type='Linear', myopacity=1.0):
    s = QgsRasterShader()
    #Then we instantiate the specialized ramp shader object:
    c = QgsColorRampShader()
    #We must name a type for the ramp shader. In this case we use an interpolatedshader:
    if (type=='Linear'): c.setColorRampType(QgsColorRampShader.Interpolated)
    if (type=='Discrete'): c.setColorRampType(QgsColorRampShader.Discrete)
    if (type=='Exact'): c.setColorRampType(QgsColorRampShader.Exact)
    #Now we’ll create a list hold our color ramp definition:
    i = []
    #Then we populate the list with color ramp color values corresponding to elevation value ranges:
    for label, (color, limite) in dict.items():
        i.append(QgsColorRampShader.ColorRampItem(limite, color, label)) #QColor(color), label))
    #Now we assign the color ramp to our shader:
    c.setColorRampItemList(i)
    #Now we tell the generic raster shader to use the color ramp:
    s.setRasterShaderFunction(c)
    #Next we create a raster renderer object with the shader:
    ps = QgsSingleBandPseudoColorRenderer(lyr.dataProvider(), 1, s)
    #We assign the renderer to the raster layer:
    lyr.setRenderer(ps)
    # opacity
    lyr.renderer().setOpacity(myopacity)
    #Finally we add the layer to the canvas to view it:
    lyr.triggerRepaint()
    # should not be necessary
    iface.layerTreeView().refreshLayerSymbology(lyr.id())
    return lyr

#######################################################  raster color composite

# bands of fn (in order): e.g. bandNames=['band2','band3','band4','band8']
# color composite dictionary: e.g. myRGB={'R':'band8', 'G':'band4','B':'band3'}
# K=number of standard deviations
def set_mean_std_color_composite(rlayer,bandNames,myRGB,K,myopacity=1.0):
    for channel, band in myRGB.items():
        print(channel,band)
        # the band of the original multiband raster that corresponds to 'channel' (R,G, or B)
        idxBand=bandNames.index(myRGB[channel])+1 # +1 since bands indices start at 1
        if channel=='R': rlayer.renderer().setRedBand(idxBand)
        if channel=='G': rlayer.renderer().setGreenBand(idxBand)
        if channel=='B': rlayer.renderer().setBlueBand(idxBand)
        stats = rlayer.dataProvider().bandStatistics(idxBand)
        band_type = rlayer.renderer().dataType(idxBand) # not sure why is necessary, but it is
        enhancement = QgsContrastEnhancement(band_type)
        enhancement.setMaximumValue(stats.mean+K*stats.stdDev)
        enhancement.setMinimumValue(stats.mean-K*stats.stdDev)
        enhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
        if channel=='R': rlayer.renderer().setRedContrastEnhancement(enhancement)
        if channel=='G': rlayer.renderer().setGreenContrastEnhancement(enhancement)
        if channel=='B': rlayer.renderer().setBlueContrastEnhancement(enhancement)
    # if we want to set opacity
    rlayer.renderer().setOpacity(myopacity)
    rlayer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(rlayer.id())
    return rlayer


###################### my_processing_run
# operation: string that defines the operation to apply from Processing Toolbox
# ln_input: string: layer name of the input layer
# dict_params: dictionary with operation parameters except 'INPUT' and 'OUTPUT'
# layer_name: name of the output layer
# output: output layer
def my_processing_run(operation,ln_input,dict_params,layer_name):
    dict_params['INPUT']=ln_input
    dict_params['OUTPUT']=QgsProcessing.TEMPORARY_OUTPUT
    mylayer=processing.run(operation,dict_params)['OUTPUT']
    # if mylayer is a string
    if isinstance(mylayer,str):
        if 'tif' in mylayer:
            mylayer=my_add_raster_layer(mylayer,layer_name)
        else:
            mylayer=my_add_vector_layer(mylayer,layer_name)
    else:
        myproject.addMapLayer(mylayer)
    mylayer.setName(layer_name)
    return mylayer

################################### add, name, remove layers

# It supposes there is a myproject variable
# add and name vector layer from file
# fn: string: path_to_file
# ln: string: output layer name
# output: output layer
def my_add_vector_layer(fn,ln):
    mylayer=QgsVectorLayer(fn,"", "ogr")
    mylayer.setName(ln)
    myproject.addMapLayer(mylayer)
    return mylayer

def my_add_raster_layer(fn,ln):
    mylayer=QgsRasterLayer(fn,"", "gdal")
    mylayer.setName(ln)
    myproject.addMapLayer(mylayer)
    return mylayer

# It supposes there is a myproject variable
# remove layer with name "ln"
def my_remove_layer(ln):
    to_be_deleted = myproject.mapLayersByName(ln)[0]
    myproject.removeMapLayer(to_be_deleted.id())

def add_vlayer_to_group(FOLDER_FN, LN, GN,LG):
    mygroup = root.findGroup(GN)
    mylayer=QgsVectorLayer(FOLDER_FN,LN, "ogr")
    if LG is not None: legenda(mylayer,LG['atrib'],LG['params'])
    myproj.addMapLayer(mylayer, False)
    mygroup.addLayer(mylayer)
    return mylayer.crs().authid()

def add_rlayer_to_group(FOLDER_FN, LN,  GN):
    mygroup = root.findGroup(GN)
    mylayer=QgsRasterLayer(FOLDER_FN,LN)
    myproj.addMapLayer(mylayer, False)
    mygroup.addLayer(mylayer)
    return mylayer.crs().authid()


# It supposes there is a myproject variable
# clear layer tree and canvas
def my_clean_project():
    # project and canvas
    myproject = QgsProject.instance() # does not write to file
    mycanvas = iface.mapCanvas()
    # clear layers in project
    myproject.removeAllMapLayers()
    # refresh canvas
    mycanvas.refreshAllLayers()
    return myproject,mycanvas

################# file manipulation: change file encoding to utf-8
# input: fn is the file name with path
# output: the original encoding of fn: the file fn is going to be overwritten
# Extra pre-processing: we suppose that separators are not spaces and we want to get rid of spaces
def convert_encoding_to_utf8(fn):
    from chardet import detect
    parent=iface.mainWindow()
    with open(fn, 'rb') as f:
        content_bytes = f.read()
    detected = detect(content_bytes)
    encoding = detected['encoding']
    if encoding!='utf-8':
        answer=QMessageBox.question(parent,'Question', f'Encoding is {encoding}. Do you want to overwite using UTF-8?' )
        if answer==QMessageBox.Yes: 
            content_text = content_bytes.decode(encoding)
            with open(fn, 'w') as f:
                f.write(content_text.replace("\r\n","\n").replace(' ' ,''))
    return encoding


###################### vector layer geometry: access and edit coordinates 
# Edit layer and round vertices to ndigits (Problem suggested by Miguel)
# inputs: layer to edit (dimension 2 and Multipart) and number of digits of vertices in the output
# output: edited vector layer
# The idea is:
# 1. Read as above the layer coordinates
# 2. Change them as we wish
# 3. For each feature, put everything together in a wkt string 
# 4. replacing the old feature by the new one
# 5. Update each feature and the layer.
def round_vertices_coordinates_multipolygon(vlayer,ndigits):
    with edit(vlayer):
        for feat in vlayer.getFeatures():
            mystr='MultiPolygon('
            f=feat.geometry().asMultiPolygon()
            for part in f:
                mystr=mystr+'('
                for ring in part:
                    mystr=mystr+'('
                    for v in ring:
                        mystr=mystr+str(round(v.x(),ndigits))+' '+ str(round(v.y(),ndigits))+','
                    mystr=mystr+'),'
                mystr=mystr+'),'
            mystr=mystr+')'
            #print(mystr)
            mystr.replace(',)',')')
            mygeometry = QgsGeometry.fromWkt(mystr)
            feat.setGeometry(mygeometry)
            vlayer.updateFeature(feat)
            vlayer.updateExtents() 
    return vlayer

########################################### create layer from result of SQL query

# input : 
# 1) result from SQL query; 
# 2) dictionary, where each key is an attribute. 
# 3) integer: crs epsg code for the output layer
# output: if 'geom' is one key of the dictionary, new vector layer from result

def create_layer_from_sql_spatial_result(result,myoutputdict,mycrs):
    L=list(myoutputdict) # list of attributes for output layer (including 'geom')
    if L==[] or 'geom' not in L:
        print(result)
        # Suggestion: convert "result" into a delimited text layer

    # Create output spatial layer
    if L!=[] and 'geom' in L:
        # Determine geometry for output layer
        idx_geom=L.index('geom') # index of 'geom' in "result"
        myoutputgeometry= myoutputdict['geom']
        # removes'geom' from output attributes
        myoutputdict.pop('geom')
        # Convert "result" into a new vector layer
        # Create empty layer with the correct geometry
        mylayer = QgsVectorLayer(myoutputgeometry, '', "memory")
        mylayer.setName(ln)
        pr = mylayer.dataProvider()
        # create new atributes (except 'geom')
        if not myoutputdict=={}:
            pr.addAttributes(list(myoutputdict.values())) # extract values from dict
            mylayer.updateFields() # “update-after-change”.
        # change CRS
        crs=mylayer.crs()
        crs.createFromId(mycrs)
        mylayer.setCrs(crs)
        
        # Populate mylayer with values in "result"
        with edit(mylayer):
            for row in result:
                # create new feature
                feat=QgsFeature()
                # feature's geometry
                mystr=row[idx_geom] # geometry
                mygeometry = QgsGeometry.fromWkt(mystr)
                feat.setGeometry(mygeometry)
                #feature's attributes # remainging values
                row.remove(mystr)
                if len(row)>0:
                    feat.setAttributes(row) 
                # add feature to dataProvider
                ok=pr.addFeature(feat) 
                mylayer.updateExtents() # “update-after-change”.

        # return new layer
        return mylayer

######################################################### add layer to existing geopackage
def add_layer_to_geopackage(fn,ln):
    processing.run("native:package", 
    {'LAYERS':[ln],
    'OUTPUT': fn,
    'OVERWRITE':False,
    'SAVE_STYLES':True,
    'SAVE_METADATA':True,
    'SELECTED_FEATURES_ONLY':False})

######################################################### get layer from geopackage
# fn: string: path and file name of geopackage
# ln: string: layer name to be added to geopackage
def add_gpkg_layer(fn, ln):
    layers = [l.GetName() for l in ogr.Open(fn)]
    if ln in layers:
        fn_new=fn + "|layername=" + ln # layername within geopackage
        my_add_vector_layer(fn_new,ln)
    else: 
        print('Error: there is no layer named "{}" in {}!'.format(layer, gpkg))


# requires sklearn
# my_array: numpy nd array - holds image with Nrow*Ncol pixels and Nbands bands
# k: number of clusters to create
# sample_rate: proportion of pixels used to train kmeans
def my_kmeans(my_array,k,sample_rate):
    # data analysis with sklearn
    from sklearn.cluster import KMeans # clusters with KMeans
    from sklearn.utils import shuffle # to extract a sub sample of the data
    # create data array: rows are pixels; columns are bands
    Nrow=my_array.shape[1]
    Ncol=my_array.shape[2]
    Nbands=my_array.shape[0]
    # create array with the right shape but filled with zeros
    X = np.zeros(shape=(Nrow*Ncol,Nbands))
    print(X.shape)
    # fill X with pixel values (1 column per band)
    for i in range(Nbands):
        X[:,i]=my_array[i].flatten()
    # sample using function shuffle from sklearn
    X_sample = shuffle(X, random_state=0)[:int(Nrow*Ncol*sample_rate)]
    # apply KMeans
    kmeans = KMeans(n_clusters=k, random_state=0).fit(X_sample)
    # determine pixel labels
    labels = kmeans.predict(X)
    # reshape as original image and return
    return labels.reshape(Nrow,Ncol)

###################################################### gdal 
# fn: string: ffilename of input raster
# fn_new: string: file name of output raster
# nbands: integer: number of bands of output raster
# requires gdal and osr from osgeo
def create_new_empty_raster_from_filename(fn,fn_new,nbands):
    # create raster layer from fn
    rlayer=QgsRasterLayer(fn,"", "gdal")
    # also, access data with gdal.Open, read mode
    gdal_layer = gdal.Open(fn, gdal.GA_ReadOnly) 
    # determine coordinate transformation with gdal
    geotransform = gdal_layer.GetGeoTransform()   # from osgeo.gdal.Dataset object
    # determine raster size
    W=rlayer.width() # from QgsRasterLayer object
    H=rlayer.height() # from QgsRasterLayer object
    # determine CRS
    EPSGcode=int(rlayer.crs().authid()[5:]) # from QgsRasterLayer object
    # create empty raster with gdal using parameters above with nbands
    # my_new_raster=None
    my_new_raster = gdal.GetDriverByName('GTiff').Create(fn_new,W,H,nbands,gdal.GDT_Float32)
    my_new_raster.SetGeoTransform(geotransform)
    srs=osr.SpatialReference()
    srs.ImportFromEPSG(EPSGcode)
    my_new_raster.SetProjection(srs.ExportToWkt())
    # close connection
    my_new_raster = None
    return (geotransform,W,H,EPSGcode)

# input file name of reference raster (empty raster)  #######  igual ao de cima?
# output: osgeo.gdal.Dataset with 1 band
# CRS, extent, dataType, resolution will be copied from the reference raster
def create_empty_output_from_raster_reference_file_name(fn,fn_new,nbands=1):
    referencefile = fn
    reference = gdal.Open(referencefile, gdal.GA_ReadOnly) # returns osgeo.gdal.Dataset
    referenceProj = reference.GetProjection()
    referenceTrans = reference.GetGeoTransform()
    bandreference = reference.GetRasterBand(1)  # osgeo.gdal.Band
    x = reference.RasterXSize
    y = reference.RasterYSize
    outputfile = fn_new
    driver= gdal.GetDriverByName('GTiff') # osgeo.gdal.Driver
    output = driver.Create(outputfile, x, y, nbands, datatype=gdal.GDT_Float32) # osgeo.gdal.Dataset
    output.SetGeoTransform(referenceTrans)
    output.SetProjection(referenceProj)
    output = None



# requires numpy as np
# input: string: file name of input raster (tif file) 
# returns array of values, and nodatavalue in original tif file
# array: (number_bands,number_rows,number_columns)
def create_array_from_raster_file_name(fn):
    # create raster layer from fn
    rlayer=QgsRasterLayer(fn,"", "gdal")
    # also, access data with gdal.Open
    gdal_layer = gdal.Open(fn, gdal.GA_ReadOnly) 
    # determine no data value from data provider (use 1st band)
    if not np.isnan(rlayer.dataProvider().sourceNoDataValue(1)):
        nodatavalue=int(rlayer.dataProvider().sourceNoDataValue(1)) # from QgsRasterLayer object
    else:
        nodatavalue=np.nan
    my_array=gdal_layer.ReadAsArray()
    # convert nodatavalues into numpy.nan
    if not np.isnan(nodatavalue):
        my_array[my_array==nodatavalue]=np.nan
    return (my_array,nodatavalue)


##!!!!!! DOES NOT WORK
## bandreference.DataType, ou gdal.GDT_Float32
#def fill_empty_raster_with_array_values(fn,myarray,fn_out, datatype=gdal.GDT_Float32):
#    dataset = gdal.Open(fn, gdal.GA_Update) 
#    referenceProj = dataset.GetProjection()
#    referenceTrans = dataset.GetGeoTransform()
#    x = dataset.RasterXSize
#    y = dataset.RasterYSize
#    # write processed data to myraster
#    output = gdal.GetDriverByName('GTiff').Create(fn_out, x, y, 1, datatype)
#    output.SetGeoTransform(referenceTrans)
#    output.SetProjection(referenceProj)
#    output.GetRasterBand(1).WriteArray(myarray)
#    # assign nodatavalue to myraster
#    #myraster.GetRasterBand(1).SetNoDataValue(nodatavalue)
#    # close connection
#    output = None
#    mylayer=QgsRasterLayer(fn_out,"", "gdal")
#    return mylayer
#

# resample
# from https://gis.stackexchange.com/questions/296770/aligning-many-rasters-using-pyqgis-or-python
def resample_raster_fn_to_fnout_using_fnref(fn,fnref,fnout,nbands=1):
    inputfile = fn
    input = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    inputProj = input.GetProjection()
    inputTrans = input.GetGeoTransform()
    referencefile = fnref
    reference = gdal.Open(referencefile, gdalconst.GA_ReadOnly)
    referenceProj = reference.GetProjection()
    referenceTrans = reference.GetGeoTransform()
    bandreference = reference.GetRasterBand(1)    
    x = reference.RasterXSize
    y = reference.RasterYSize
    # creates new file 
    outputfile = fnout
    driver= gdal.GetDriverByName('GTiff')
    output = driver.Create(outputfile, x, y, nbands, bandreference.DataType)
    output.SetGeoTransform(referenceTrans)
    output.SetProjection(referenceProj)
    # resample 
    gdal.ReprojectImage(input, output, inputProj, referenceProj, gdalconst.GRA_NearestNeighbour) #gdalconst.GRA_Bilinear)
    del output

##################### reproject with rasterio
# import rasterio
# from rasterio.warp import reproject, Resampling, calculate_default_transform
# https://pygis.io/docs/e_raster_reproject.html
# e.g. dst_crs = "EPSG:3857"  -- this is returned by rlayer.crs().authid()
# fin: path/file_in.tif
# fout: path/file_out.tif
def reproject_rasterio(fin, fout, dst_crs):
    with rasterio.open(fin) as src:
        src_transform = src.transform
        # calculate the transform matrix for the output
        dst_transform, width, height = calculate_default_transform(
            src.crs,
            dst_crs,
            src.width,
            src.height,
            *src.bounds,  # unpacks outer boundaries (left, bottom, right, top)
        )
        # set properties for output
        dst_kwargs = src.meta.copy()
        dst_kwargs.update(
            {
                "crs": dst_crs,
                "transform": dst_transform,
                "width": width,
                "height": height,
                "nodata": 0,  # replace 0 with np.nan
            }
        )
        with rasterio.open(fout, "w", **dst_kwargs) as dst:
            # iterate through bands
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )




################### find files in folder (correção trabalho cadastro maio 2022)
# find files with regex
# myfolder: where the files are
# stregex: regex string
def find_files(myfolder, stregex,pick_attribute=''): 
    myregex=re.compile(stregex.lower())
    # same as glob?
    myfiles=[]
    myfilesfull=[]
    myroots=[]
    myrootsup=[]
    myrootsupup=[]
    for (root, dirs, file) in os.walk(myfolder,topdown=True):
        for f in file:
            myfiles.append(os.path.join(f))
            myfilesfull.append(os.path.join(root,f))
            myroots.append(os.path.split(root)[1])
            myrootsup.append(os.path.split(os.path.split(root)[0])[1])
            myrootsupup.append(os.path.split(os.path.split(os.path.split(os.path.split(root)[0])[0])[0])[1])
    logical=[myregex.search(f.lower()) is not None for f in myfiles]
    # no files satisfy myregex:
    if sum(logical)==0:
        return None
    isqml=[re.compile(r'.*qml$').search(f.lower()) is not None for f in myfiles]
    myfn=[myfilesfull[i] for i in range(len(myfiles)) if logical[i]]
    myln=[myfiles[i] for i in range(len(myfiles)) if logical[i]]
    myqml=[myfilesfull[i] for i in range(len(myfiles)) if isqml[i]]
    myoptions=[myfiles[i]+' --- '+myrootsupup[i]+'/'+myrootsup[i]+'/'+myroots[i] for i in range(len(logical)) if logical[i]]
    myoption, ok = QInputDialog.getItem(parent, "select:", stregex, myoptions, 0, False)
    idxoption=myoptions.index(myoption)
    myfnfull=myfn[idxoption]
    ln=myln[idxoption]
    if 'tif' in stregex:
        # to extract tif from gpkg
        if 'gpkg' in myfnfull:
            try: 
                if len(myqml) >0 and 'cossim' in stregex.lower():
                    dst_file=os.path.join(os.path.dirname(myfnfull),os.path.splitext(ln)[0]+'.qml')
                    if not dst_file == myqml[0]:
                        shutil.copy(myqml[0], dst_file)
            except:
                pass
            my_add_raster_layer(myfnfull,ln)
            return myfnfull
        else:
            try: 
                if len(myqml) >0 and 'cossim' in stregex.lower():
                    dst_file=os.path.join(os.path.dirname(myfnfull),os.path.splitext(ln)[0]+'.qml')
                    if not dst_file == myqml[0]:
                        shutil.copy(myqml[0], dst_file)
            except:
                pass
            my_add_raster_layer(myfnfull,ln)
            return myfnfull
    # read simple table 
    if 'gpkg' not in myfnfull and ('txt' in myfnfull or 'csv' in myfnfull):
        fn_layer=myfnfull
        vlayer=QgsVectorLayer(fn_layer,'fn_layer','ogr')
        for f in vlayer.getFeatures(): 
                feat=f
                break # just keep 1st
        atnames=vlayer.dataProvider().fields().names()
        vals=[feat[attrib] for attrib in atnames]
        QMessageBox.information(parent,'atributos', ' -- '.join(atnames)+'\n *** \n' +' -- '.join(map(str,vals)))
        return fn_layer
    # to extract table from gpkg
    if 'gpkg' in myfnfull and ('txt' in stregex or 'csv' in stregex):
        fn_layer=myfnfull+'|layername='+os.path.splitext(ln)[0]
        vlayer=QgsVectorLayer(fn_layer,'fn_layer','ogr')
        for f in vlayer.getFeatures(): 
                feat=f
                break # just keep 1st
        atnames=vlayer.dataProvider().fields().names()
        vals=[feat[attrib] for attrib in atnames]
        QMessageBox.information(parent,'atributos', ' -- '.join(atnames)+'\n *** \n' +' -- '.join(map(str,vals)))
        return fn_layer
    else:
        if 'gpkg' in stregex or 'shp' in stregex:
            vlayer=QgsVectorLayer(myfnfull,'myfnfull','ogr')
            # verify if geometry is valid
            ckeck_and_fix_load_vlayer_validity(myfnfull,ln)
            # list attribute names and values for the 1st feature    
            for f in vlayer.getFeatures(): 
                feat=f
                break # just keep 1st
            atnames=vlayer.dataProvider().fields().names()
            vals=[feat[attrib] for attrib in atnames]
            QMessageBox.information(parent,'atributos', ' -- '.join(atnames)+'\n *** \n' +' -- '.join(map(str,vals)))
            # pick attribute
            if pick_attribute is not '':
                myoptions=atnames
                atname, ok = QInputDialog.getItem(parent, 'Escolher' , pick_attribute, myoptions, 0, False)
                idx = vlayer.fields().indexOf(atname)
                myListValues = list(vlayer.uniqueValues(idx)) # uniqueValues returns a "set"
                if isinstance(myListValues[0],str):
                    myListValues.extend(['1','9999'])
                else:
                    myListValues.extend([1,9999])
                val, ok = QInputDialog.getItem(parent, 'Escolher valor' , pick_attribute, map(str,myListValues), 0, False)
                if str(val)=='9999':
                    stop
                if isinstance(myListValues[0],str):
                    return myfnfull,atname,'"'+atname+'"=\''+str(val)+'\''
                else:
                    return myfnfull,atname, '"'+atname+'"='+val
            else:
                return myfnfull

