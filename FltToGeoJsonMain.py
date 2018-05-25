#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/18 9:59
'''

import os
import sys
import numpy
import ast
import shutil
try:
    from osgeo import gdal, ogr
except ImportError:
    import gdal
import flt.flttoshp as flttoshp
import flt.shpToGeoJson as shpToGeoJson
import util.reprojectShp as reprojectShp

classified = [(0, 0, 0.013435),
                (1, 0.013435, 0.037422),
                (2, 0.037422, 0.080247),
                (3, 0.080247, 0.156709),
                (4, 0.156709, 0.293223),
                (5, 0.293223, 0.536956),
                (6, 0.536956, 0.972118),
                (7, 0.972118, 1.749056),
                (8, 1.749056, 3.136204),
                (9, 3.136204, 5.612822)]
def fltToGeoJson(fltpath, classify, outGeoJsonPath):
    # 下面路径为中间结果路径，程序运行结束后，删除
    root = sys.path[0]
    tempParent = 'testdata/temp'
    if not os.path.exists(root + '/' + tempParent):
        os.makedirs(root + '/' + tempParent)
    tempFltToTifPath = root + '/' + tempParent + '/flttotif.tif'
    classifyTifPath = root + '/' + tempParent + '/classified.tif'
    maskTifPath = root + '/' + tempParent + '/mask.tif'
    tempTifToShpPath = root + '/' + tempParent + '/flttoshp.shp'
    ogr2ogrPath = root + '/gdal223/ogr2ogr.py'

    flttoshp.fltToShp(fltpath, tempFltToTifPath, classify, classifyTifPath, maskTifPath, tempTifToShpPath)

    # 重投影
    # 复制一份输出的shp图，并删除原来的，对复制后数据进行投影，并输出到新shp图
    reprojectShpPath = tempTifToShpPath[: tempTifToShpPath.rfind('.')] + '_reproject.' + tempTifToShpPath[tempTifToShpPath.rfind('.') + 1:]
    reprojectCalcShpPath = tempTifToShpPath[: tempTifToShpPath.rfind('.')] + '_reproject_calc.' + tempTifToShpPath[tempTifToShpPath.rfind('.') + 1:]
    driver = ogr.GetDriverByName('ESRI Shapefile')
    tempTifToShpDatasource = None # 将打开的shp datastore置空，为了删除
    reprojectShp.reproject(tempTifToShpPath, 102025, reprojectShpPath) #epsg:102025为Asia_North_Albers_Equal_Area_Conic等面积投影，用于面积计算
    if os.access(tempTifToShpPath, os.F_OK):
        driver.DeleteDataSource(tempTifToShpPath)
    # 增加计算面积功能
    flttoshp.calcShpArea(reprojectShpPath, reprojectCalcShpPath)

    reprojectShp.reproject(reprojectCalcShpPath, 4326, tempTifToShpPath)
    # 处理输出文件目录，保证输出目录存在
    outGeoJsonPath = outGeoJsonPath.replace('\\', '/')
    targetFolder = outGeoJsonPath[0 : outGeoJsonPath.rfind('/')]
    if not os.path.exists(targetFolder):
        os.makedirs(targetFolder)
    shpToGeoJson.exportShpToGeoJson(ogr2ogrPath, tempTifToShpPath, outGeoJsonPath)
    shutil.rmtree(root + '/' + tempParent)

if __name__ == '__main__':
    gdal.AllRegister()
    argvs = gdal.GeneralCmdLineProcessor(sys.argv)
    if argvs is None:
        sys.exit(0)

    # test instance
    root = os.getcwd()
    fltpath = root + '/testdata/rain_2016.flt'
    classify = classified
    outGeoJsonPath = root + '/testdata/out/shpToJson.json'
    fltToGeoJson(fltpath, classify, outGeoJsonPath)

    # print('argv 0: ' + argvs[0])
    # print('argv 1: ' + argvs[1].split('=')[1])
    # print('argv 2: ' + argvs[2].split('=')[1])
    # print('argv 3: ' + argvs[3].split('=')[1])
    #
    # fltpath = argvs[1].split('=')[1]
    # classifyString = argvs[2].split('=')[1]
    # classifyList = ast.literal_eval(classifyString)
    # classify = numpy.array(classifyList)
    # outGeoJsonPath = argvs[3].split('=')[1]
    # fltToGeoJson(fltpath, classify, outGeoJsonPath)
