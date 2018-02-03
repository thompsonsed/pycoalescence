
.. _program_listing_file_Map.cpp:

Program Listing for File Map.cpp
========================================================================================

- Return to documentation for :ref:`file_Map.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details
   #include "Map.h"
   #include "Setup.h"
   
   void Map::setDims(SimParameters mapvarsin)
   {
       if(!checksetdim)  // checks to make sure it hasn't been run already.
       {
           mapvars = mapvarsin;
           deme = mapvarsin.deme;
           xdim = mapvarsin.vargridxsize;
           ydim = mapvarsin.vargridysize;
           scale = mapvarsin.varcoarsemapscale;
           nUpdate = 0;
           checksetdim = true;
           dUpdateTime = 0;
           dPristine = mapvarsin.dPristine;
           if(dPristine == 0)
           {
               dPristine = 0.000000000000000001;
           }
           dForestTransform = mapvarsin.dForestChangeRate;
           landscape_type = mapvarsin.landscape_type;
       }
       else
       {
           cerr << "ERROR_MAP_001: Dimensions have already been set" << endl;
           return;
       }
       return;
   }
   
   bool Map::checkMapExists()
   {
       for(unsigned int i = 0; i < mapvars.configs.getSectionOptionsSize(); i++)
       {
           string tmppath = mapvars.configs[i].getOption("path");
           if(!doesExistNull(tmppath))
           {
               return (false);
           }
       }
       return (true);
   }
   
   void Map::calcFineMap()
   {
       string fileinput = mapvars.finemapfile;
       unsigned long mapxsize = mapvars.varfinemapxsize;
       unsigned long mapysize = mapvars.varfinemapysize;
       if(!checksetdim)  // checks that the dimensions have been set.
       {
           throw Map_Exception("ERROR_MAP_002: dimensions not set.");
       }
       // Note that the default "null" type is to have 100% forest cover in every cell.
       #ifndef SIZE_LIMIT
       if(mapxsize > 1000000 || mapysize > 1000000)
       {
           throw runtime_error("Extremely large map sizes set for " + fileinput + ": " + to_string(mapxsize) + ", " + to_string(mapysize) + "\n");
       }
       #endif
       Matrix<float> toret;
       toret.SetSize(mapysize, mapxsize);
       fine_map.SetSize(mapysize, mapxsize);
   #ifdef DEBUG
       cerr << "Calculating fine map" << endl;
   #endif
       if(fileinput == "null")
       {
           for(unsigned long i = 0; i < mapysize; i++)
           {
               for(unsigned long j = 0; j < mapxsize; j++)
               {
                   toret[i][j] = 1.0;
               }
           }
       }
       else  // There is a map to read in.
       {
           toret.import(fileinput);
       }
   #ifdef DEBUG
       cerr << "import complete" << endl;
   // os << toret << endl;
   #endif
       iFineForestMax = 0;
   
       for(unsigned long i = 0; i < mapysize; i++)
       {
           for(unsigned long j = 0; j < mapxsize; j++)
           {
               fine_map[i][j] = (unsigned long)(max((double)round(toret[i][j] * deme), 0.0));
               if(fine_map[i][j] > iFineForestMax)
               {
                   iFineForestMax = fine_map[i][j];
               }
           }
       }
   }
   
   void Map::calcPristineFineMap()
   {
       string fileinput = mapvars.pristinefinemapfile;
       unsigned long mapxsize = mapvars.varfinemapxsize;
       unsigned long mapysize = mapvars.varfinemapysize;
       if(!checksetdim)  // checks that the dimensions have been set.
       {
           throw Map_Exception("ERROR_MAP_002: dimensions not set.");
       }
       #ifndef SIZE_LIMIT
       if(mapxsize > 1000000 || mapysize > 1000000)
       {
           throw runtime_error("Extremely large map sizes set for " + fileinput + ": " + to_string(mapxsize) + ", " + to_string(mapysize) + "\n");
       }
       #endif
       // Note that the default "null" type is to have 100% forest cover in every cell.
       Matrix<float> toret;
       hasPristine = true;
       iPristineFineForestMax = 0;
       if(fileinput == "null")
       {
           toret.SetSize(mapysize, mapxsize);
           pristine_fine_map.SetSize(mapysize, mapxsize);
           for(unsigned long i = 0; i < mapxsize; i++)
           {
               for(unsigned long j = 0; j < mapysize; j++)
               {
                   toret[j][i] = 1.0;
               }
           }
       }
       else if(fileinput == "none")
       {
           hasPristine = false;
       }
       else  // There is a map to read in.
       {
           toret.SetSize(mapysize, mapxsize);
           pristine_fine_map.SetSize(mapysize, mapxsize);
           toret.import(fileinput);
       }
       // os << toret << endl;
       if(hasPristine)
       {
           for(unsigned long i = 0; i < mapysize; i++)
           {
               for(unsigned long j = 0; j < mapxsize; j++)
               {
                   pristine_fine_map[i][j] = (unsigned long)(max((double)round(toret[i][j] * deme), 0.0));
                   if(pristine_fine_map[i][j] > iPristineFineForestMax)
                   {
                       iPristineFineForestMax = pristine_fine_map[i][j];
                   }
               }
           }
       }
       return;
   }
   
   void Map::calcCoarseMap()
   {
       string fileinput = mapvars.coarsemapfile;
       unsigned long mapxsize = mapvars.varcoarsemapxsize;
       unsigned long mapysize = mapvars.varcoarsemapysize;
       if(!checksetdim)  // checks that the dimensions have been set.
       {
           throw Map_Exception("ERROR_MAP_003: dimensions not set.");
       }
       #ifndef SIZE_LIMIT
       if(mapxsize > 1000000 || mapysize > 1000000)
       {
           throw runtime_error("Extremely large map sizes set for " + fileinput + ": " + to_string(mapxsize) + ", " + to_string(mapysize) + "\n");
       }
       #endif
       // Note that the default "null" type for the coarse type is to have a density of 1 in every cell. "none" defaults to no
       // pristine map
       Matrix<float> toret;
       bCoarse = true;
       iCoarseForestMax = 0;
       if(fileinput == "null")
       {
           toret.SetSize(mapysize, mapxsize);
           coarse_map.SetSize(mapysize, mapxsize);
           for(unsigned long i = 0; i < mapxsize; i++)
           {
               for(unsigned long j = 0; j < mapysize; j++)
               {
                   toret[j][i] = 1.0;
               }
           }
       }
       else if(fileinput == "none")
       {
           bCoarse = false;
       }
       else  // There is a map to read in.
       {
           toret.SetSize(mapysize, mapxsize);
           coarse_map.SetSize(mapysize, mapxsize);
           toret.import(fileinput);
       }
       if(bCoarse)
       {
           for(unsigned long i = 0; i < mapysize; i++)
           {
               for(unsigned long j = 0; j < mapxsize; j++)
               {
                   coarse_map[i][j] = (unsigned long)(max((double)round(toret[i][j] * deme), 0.0));
                   if(coarse_map[i][j] > iCoarseForestMax)
                   {
                       iCoarseForestMax = coarse_map[i][j];
                   }
               }
           }
       }
       return;
   }
   
   void Map::calcPristineCoarseMap()
   {
       //  os << "pristine coarse map file: " << mapvars.pristinecoarsemapfile << endl;
       string fileinput = mapvars.pristinecoarsemapfile;
       unsigned long mapxsize = mapvars.varcoarsemapxsize;
       unsigned long mapysize = mapvars.varcoarsemapysize;
       if(!checksetdim)  // checks that the dimensions have been set.
       {
           throw Map_Exception("ERROR_MAP_003: dimensions not set.");
       }
       #ifndef SIZE_LIMIT
       if(mapxsize > 1000000 || mapysize > 1000000)
       {
           throw runtime_error("Extremely large map sizes set for " + fileinput + ": " + to_string(mapxsize) + ", " + to_string(mapysize) + "\n");
       }
       #endif
       // Note that the default "null" type for the coarse type is to have non-forest in every cell.
       Matrix<float> toret;
       iPristineCoarseForestMax = 0;
       if(bCoarse)
       {
           if(fileinput == "null")
           {
               toret.SetSize(mapysize, mapxsize);
               pristine_coarse_map.SetSize(mapysize, mapxsize);
               for(unsigned long i = 0; i < mapxsize; i++)
               {
                   for(unsigned long j = 0; j < mapysize; j++)
                   {
                       toret[j][i] = 1.0;
                   }
               }
           }
           else if(fileinput == "none")
           {
               hasPristine = false;
           }
           else  // There is a map to read in.
           {
               toret.SetSize(mapysize, mapxsize);
               pristine_coarse_map.SetSize(mapysize, mapxsize);
               toret.import(fileinput);
           }
       }
       if(bCoarse && hasPristine)
       {
           for(unsigned long i = 0; i < mapysize; i++)
           {
               for(unsigned long j = 0; j < mapxsize; j++)
               {
                   pristine_coarse_map[i][j] = (unsigned long)(max((double)round(toret[i][j] * deme), 0.0));
                   if(pristine_coarse_map[i][j] > iPristineCoarseForestMax)
                   {
                       iPristineCoarseForestMax = pristine_coarse_map[i][j];
                   }
               }
           }
       }
       return;
   }
   
   void Map::setTimeVars(double dPristinein, double dForestTransformin)
   {
       dUpdateTime = 0;
       dPristine = dPristinein;
       dForestTransform = dForestTransformin;
   }
   
   void Map::calcOffset()
   {
       if(mapvars.autocorrel_file != "null")
       {
           mapvars.setPristine(0);
       }
       //  os << mapvars.autocorrel_file << endl;
       if(fine_map.GetCols() == 0 || fine_map.GetRows() == 0)
       {
           throw Map_Exception("ERROR_MAP_004: fine map not set.");
       }
       if(coarse_map.GetCols() == 0 || coarse_map.GetRows() == 0)
       {
           if(bCoarse)
           {
               coarse_map.SetSize(fine_map.GetRows(), fine_map.GetCols());
           }
           //      throw Map_Exception("ERROR_MAP_004: coarse map not set.");
       }
       finexoffset = mapvars.varfinemapxoffset + mapvars.varsamplexoffset;
       fineyoffset = mapvars.varfinemapyoffset + mapvars.varsampleyoffset;
       coarsexoffset = mapvars.varcoarsemapxoffset;
       coarseyoffset = mapvars.varcoarsemapyoffset;
       scale = mapvars.varcoarsemapscale;
       // this is the location of the top left (or north west) corner of the respective map
       // and the x and y distance from the top left of the grid object that contains the initial lineages.
       finexmin = -finexoffset;
       fineymin = -fineyoffset;
       finexmax = finexmin + (fine_map.GetCols());
       fineymax = fineymin + (fine_map.GetRows());
       if(bCoarse) // Check if there is a coarse map
       {
           coarsexmin = -coarsexoffset - finexoffset;
           coarseymin = -coarseyoffset - fineyoffset;
           coarsexmax = coarsexmin + scale * (coarse_map.GetCols());
           coarseymax = coarseymin + scale * (coarse_map.GetRows());
       }
       else // Just set the offsets to the same as the fine map
       {
           coarsexmin = finexmin;
           coarseymin = fineymin;
           coarsexmax = finexmax;
           coarseymax = fineymax;
           scale = 1;
       }
       dispersal_relative_cost = mapvars.dispersal_relative_cost;
   #ifdef DEBUG
       stringstream os;
       os << "finex: " << finexmin << "," << finexmax << endl;
       os << "finey: " << fineymin << "," << fineymax << endl;
       os << "coarsex: " << coarsexmin << "," << coarsexmax << endl;
       os << "coarsey: " << coarseymin << "," << coarseymax << endl;
       os << "offsets: "
            << "(" << finexoffset << "," << fineyoffset << ")(" << coarsexoffset << "," << coarseyoffset << ")" << endl;
       os << "pristine fine file: " << pristine_fine_map << endl;
       os << "pristine coarse file: " << pristine_coarse_map << endl;
       write_cout(os.str());
   #endif
       //      os << "fine variables: " << finexmin << "," << finexmax << endl;
       //      os << "coarse variabes: " << coarsexmin << "," << coarsexmax << endl;
       if(finexmin < coarsexmin || finexmax > coarsexmax || (finexmax - finexmin) < xdim || (fineymax - fineymin) < ydim)
       {
           throw Map_Fatal_Exception(
               "ERROR_MAP_006: FATAL - fine map extremes outside coarse map or sample grid larger than fine map");
       }
       return;
   }
   
   void Map::validateMaps()
   {
       stringstream os;
       os << "\rValidating maps..." << flush;
       double dTotal = fine_map.GetCols() + coarse_map.GetCols();
       unsigned long iCounter = 0;
       if(hasPristine)
       {
           if(fine_map.GetCols() == pristine_fine_map.GetCols() && fine_map.GetRows() == pristine_fine_map.GetRows() &&
              coarse_map.GetCols() == pristine_coarse_map.GetCols() && coarse_map.GetRows() == pristine_coarse_map.GetRows())
           {
               os << "\rValidating maps...map sizes okay" << flush;
               write_cout(os.str());
           }
           else
           {
               throw Map_Fatal_Exception(
                       "ERROR_MAP_009: Map validation failed - modern and pristine maps are not the same dimensions.");
           }
           for(unsigned long i = 0; i < fine_map.GetCols(); i++)
           {
               for(unsigned long j = 0; j < fine_map.GetRows(); j++)
               {
                   if(fine_map[j][i] > pristine_fine_map[j][i])
                   {
                       cerr << "fine map: " << fine_map[j][i] << "pristine map: " << pristine_fine_map[j][i]
                            << endl;
                       cerr << "x,y: " << i << "," << j << endl;
                       throw Map_Fatal_Exception("ERROR_MAP_007: Map validation failed - fine map value larger "
                                                 "than pristine fine map value.");
                   }
               }
               double dPercentComplete = 100 * ((double)(i + iCounter) / dTotal);
               if(i % 1000 == 0)
               {
                   os.str("");
                   os << "\rValidating maps..." << dPercentComplete << "%                " << flush;
                   write_cout(os.str());
               }
           }
       }
       iCounter = fine_map.GetCols();
       if(hasPristine)
       {
           for(unsigned long i = 0; i < coarse_map.GetCols(); i++)
           {
               for(unsigned long j = 0; j < coarse_map.GetRows(); j++)
               {
                   if(coarse_map[j][i] > pristine_coarse_map[j][i])
                   {
                       cerr << "coarse map: " << coarse_map[j][i] << " pristine map: " << pristine_coarse_map[j][i]
                            << endl;
                       cerr << "coarse map x+1: " << coarse_map[j][i + 1]
                            << " pristine map: " << pristine_coarse_map[j][i + 1] << endl;
                       cerr << "x,y: " << i << "," << j << endl;
                       throw Map_Fatal_Exception("ERROR_MAP_008: Map validation failed - coarse map value larger "
                                                 "than pristine coarse map value.");
                   }
               }
               double dPercentComplete = 100 * ((double)(i + iCounter) / dTotal);
               if(i % 1000 == 0)
               {
                   os.str("");
                   os << "\rValidating maps..." << dPercentComplete << "%                " << flush;
                   write_cout(os.str());
               }
           }
           
       }
       os.str("");
       os << "\rValidating maps complete                                       " << endl;
       write_cout(os.str());
   }
   
   void Map::updateMap(double generation)
   {
       // only update the map if the pristine state has not been reached.
       if(!mapvars.bPristine && hasPristine)
       {
           if(mapvars.dPristine < generation)
           {
               // Only update the map if the maps have actually changed
               if(mapvars.setPristine(nUpdate+1))
               {
                   nUpdate++;
                   // pristine_fine_map = mapvars.pristinefinemapfile;
                   // pristine_coarse_map = mapvars.pristinecoarsemapfile;
                   dCurrent = dPristine;
                   dPristine = mapvars.dPristine;
                   if(dPristine == 0)
                   {
                       dPristine = 0.000000000000000001;
                   }
                   dForestTransform = mapvars.dForestChangeRate;
                   iFineForestMax = iPristineFineForestMax;
                   fine_map = pristine_fine_map;
                   iCoarseForestMax = iPristineCoarseForestMax;
                   coarse_map = pristine_coarse_map;
                   calcPristineCoarseMap();
                   calcPristineFineMap();
                   if(hasPristine)
                   {
                       bPristine = mapvars.bPristine;
                   }
                   recalculateForestMax();
                   
                   
               }
           }
       }
   }
   
   void Map::setLandscape(string landscape_type)
   {
       if(landscape_type == "infinite")
       {
           write_cout("Setting infinite landscape.\n");
           getValFunc = &Map::getValInfinite;
       }
       else if(landscape_type == "tiled_coarse")
       {
           write_cout("Setting tiled coarse infinite landscape.\n");
           getValFunc = &Map::getValCoarseTiled;
       }
       else if(landscape_type == "tiled_fine")
       {
           write_cout("Setting tiled fine infinite landscape.\n");
           getValFunc = &Map::getValFineTiled;
       }
       else if(landscape_type == "closed")
       {
           getValFunc = &Map::getValFinite;
       }
       else
       {
           throw Fatal_Exception("Provided landscape type is not a valid option: " + landscape_type);
       }
   }
   
   unsigned long Map::getVal(
       const double& x, const double& y, const long& xwrap, const long& ywrap, const double& dCurrentGen)
   {
       return (this->*getValFunc)(x, y, xwrap, ywrap, dCurrentGen);
   }
   
   unsigned long Map::getValInfinite(
       const double& x, const double& y, const long& xwrap, const long& ywrap, const double& dCurrentGen)
   {
       double xval, yval;
       xval = x + (xdim * xwrap);  //
       yval = y + (ydim * ywrap);
       //      // return 0 if the requested coordinate is completely outside the map
       if(xval < coarsexmin || xval >= coarsexmax || yval < coarseymin || yval >= coarseymax)
       {
           return deme;
       }
       return getValFinite(x, y, xwrap, ywrap, dCurrentGen);
   }
   
   unsigned long Map::getValCoarseTiled(
       const double& x, const double& y, const long& xwrap, const long& ywrap, const double& dCurrentGen)
   {
       double newx = fmod(x + (xwrap * xdim) + finexoffset + coarsexoffset, coarse_map.GetCols());
       double newy = fmod(y + (ywrap * ydim) + finexoffset + coarsexoffset, coarse_map.GetRows());
       if(newx < 0)
       {
           newx += coarse_map.GetCols();
       }
       if(newy < 0)
       {
           newy += coarse_map.GetRows();
       }
       return getValCoarse(newx, newy, dCurrentGen);
   }
   
   unsigned long Map::getValFineTiled(
       const double& x, const double& y, const long& xwrap, const long& ywrap, const double& dCurrentGen)
   {
   
       double newx = fmod(x + (xwrap * xdim) + finexoffset, fine_map.GetCols());
       double newy = fmod(y + (ywrap * ydim) + fineyoffset, fine_map.GetRows());
       // Now adjust for incorrect wrapping behaviour of fmod
       if(newx < 0)
       {
           newx += fine_map.GetCols();
       }
       if(newy < 0)
       {
           newy += fine_map.GetRows();
       }
   #ifdef DEBUG
       if(newx >= fine_map.GetCols() || newx < 0 || newy >= fine_map.GetRows() || newy < 0)
       {
           stringstream ss;
           ss << "Fine map indexing out of range of fine map." << endl;
           ss << "x, y: " << newx << ", " << newy << endl;
           ss << "cols, rows: " << fine_map.GetCols() << ", " << fine_map.GetRows() << endl;
           throw out_of_range(ss.str());
       }
   #endif
       return getValFine(newx, newy, dCurrentGen);
   }
   
   unsigned long Map::getValCoarse(const double &xval, const double &yval, const double &dCurrentGen)
   {
       unsigned long retval = 0;
       if(hasPristine)
       {
           if(bPristine || pristine_coarse_map[yval][xval] == coarse_map[yval][xval])
           {
               return pristine_coarse_map[yval][xval];
           }
           else
           {
               double currentTime = dCurrentGen - dCurrent;
               retval = (unsigned long)floor(coarse_map[yval][xval] +
                                              (dForestTransform *
                                               ((pristine_coarse_map[yval][xval] - coarse_map[yval][xval]) /
                                                       (dPristine-dCurrent)) * currentTime));
           }
       }
       else
       {
           return coarse_map[yval][xval];
       }
   #ifdef pristine_mode
       if(retval > pristine_coarse_map[yval][xval])
           {
               string ec =
                   "Returned value greater than pristine value. Check file input. (or disable this error before "
                   "compilation.\n";
               ec += "pristine value: " + to_string((long long)pristine_coarse_map[yval][xval]) +
                     " returned value: " + to_string((long long)retval);
               throw Map_Fatal_Exception(ec);
           }
   // Note that debug mode will throw an exception if the returned value is less than the pristine state
   
   #endif
       return retval;
   }
   
   unsigned long Map::getValFine(const double&xval, const double &yval, const double& dCurrentGen)
   {
       unsigned long retval = 0;
       if(hasPristine)
       {
           if(bPristine || pristine_fine_map[yval][xval] == fine_map[yval][xval])
           {
               retval = pristine_fine_map[yval][xval];
           }
           else
           {
               double currentTime = dCurrentGen - dCurrent;
               retval = (unsigned long)floor(fine_map[yval][xval] +
                                              (dForestTransform * ((pristine_fine_map[yval][xval] - fine_map[yval][xval]) /
                                                      (dPristine-dCurrent)) * currentTime));
           }
       }
       else
       {
           return fine_map[yval][xval];
       }
   // os <<fine_map[yval][xval] << "-"<< retval << endl;
   // Note that debug mode will throw an exception if the returned value is less than the pristine state
   #ifdef pristine_mode
       if(hasPristine)
       {
           if(retval > pristine_fine_map[yval][xval])
           {
               throw Map_Fatal_Exception("Returned value greater than pristine value. Check file input. (or disable this "
                                         "error before compilation.");
           }
       }
   #endif
       return retval;
   }
   
   unsigned long Map::getValFinite(
       const double& x, const double& y, const long& xwrap, const long& ywrap, const double& dCurrentGen)
   {
   
       double xval, yval;
       xval = x + (xdim * xwrap);  //
       yval = y + (ydim * ywrap);
       //      // return 0 if the requested coordinate is completely outside the map
       if(xval < coarsexmin || xval >= coarsexmax || yval < coarseymin || yval >= coarseymax)
       {
           return 0;
       }
       if((xval < finexmin || xval >= finexmax || yval < fineymin ||
          yval >= fineymax) && bCoarse)  // check if the coordinate comes from the coarse resolution map.
       {
           // take in to account the fine map offsetting
           xval += finexoffset;
           yval += fineyoffset;
           // take in to account the coarse map offsetting and the increased scale of the larger map.
           xval = floor((xval + coarsexoffset) / scale);
           yval = floor((yval + coarseyoffset) / scale);
           return getValCoarse(xval, yval, dCurrentGen);
       }
       // take in to account the fine map offsetting
       // this is done twice to avoid having all the comparisons involve additions.
       xval += finexoffset;
       yval += fineyoffset;
       return getValFine(xval, yval, dCurrentGen);
   
   }
   
   unsigned long Map::convertSampleXToFineX(const unsigned long &x, const long &xwrap)
   {
       return x + finexoffset + (xwrap * xdim);
   }
   
   unsigned long Map::convertSampleYToFineY(const unsigned long &y, const long &ywrap)
   {
       return y + fineyoffset + (ywrap * ydim);
   }
   
   void Map::convertFineToSample(long & x, long & xwrap, long &y, long &ywrap)
   {
       double tmpx = double(x);
       double tmpy = double(y);
       convertCoordinates(tmpx, tmpy, xwrap, ywrap);
       x = floor(tmpx);
       y = floor(tmpy);
   }
   
   
   unsigned long Map::getInitialCount(double dSample, Datamask& samplemask)
   {
       unsigned long toret;
       toret = 0;
       unsigned long add = 0;
       long x, y;
       long xwrap, ywrap;
       bool printed = true;
       unsigned long max_x, max_y;
       if( samplemask.getDefault())
       {
           max_x = fine_map.GetCols();
           max_y = fine_map.GetRows();
       }
       else
       {
           max_x = samplemask.sample_mask.GetCols();
           max_y = samplemask.sample_mask.GetRows();
       }
       for(unsigned long i = 0; i < max_x; i++)
       {
           for(unsigned long j = 0; j < max_y; j++)
           {
               add = 0;
               x = i;
               y = j;
               xwrap = 0;
               ywrap = 0;
               samplemask.recalculate_coordinates(x, y, xwrap, ywrap);
               if(samplemask.getVal(x, y, xwrap, ywrap))
               {
                   add = (unsigned long) floor(dSample * (getVal(x, y, xwrap, ywrap, 0)));
               }
               toret += add;
           }
       }
       return toret;
   }
   
   SimParameters Map::getSimParameters()
   {
       return mapvars;
   }
   
   bool Map::checkMap(const double& x, const double& y, const long& xwrap, const long& ywrap, const double generation)
   {
       //       os << "CHECK: " << getVal(x,y,xwrap,ywrap) << endl;
       return getVal(x, y, xwrap, ywrap, generation) != 0;
   }
   
   bool Map::checkFine(const double& x, const double& y, const long& xwrap, const long& ywrap)
   {
       double tmpx, tmpy;
       tmpx = x + xwrap * xdim;
       tmpy = y + ywrap * ydim;
       return !(tmpx < finexmin || tmpx >= finexmax || tmpy < fineymin || tmpy >= fineymax);
   }
   
   void Map::convertCoordinates(double& x, double& y, long& xwrap, long& ywrap)
   {
       xwrap += floor(x / xdim);
       ywrap += floor(y / ydim);
       x = x - xwrap * xdim;
       y = y - ywrap * ydim;
   }
   
   unsigned long Map::runDispersal(const double& dist,
                          const double& angle,
                          long& startx,
                          long& starty,
                          long& startxwrap,
                          long& startywrap,
                          bool& disp_comp,
                          const double& generation)
   {
   // Checks that the start point is not out of matrix - this might have to be disabled to ensure that when updating the
   // map, it doesn't cause problems.
   #ifdef pristine_mode
       if(!checkMap(startx, starty, startxwrap, startywrap, generation))
       {
           disp_comp = true;
           return;
       }
   #endif
   
       // Different calculations for each quadrant to ensure that the dispersal reads the probabilities correctly.
       double newx, newy;
       newx = startx + (xdim * startxwrap) + 0.5;
       newy = starty + (ydim * startywrap) + 0.5;
       if(dispersal_relative_cost ==
          1)  // then nothing complicated is required and we can jump straight to the final point.
       {
           newx += dist * cos(angle);
           newy += dist * sin(angle);
       }
       else  // we need to see which deforested patches we pass over
       {
           long boost;
           boost = 1;
           double cur_dist, tot_dist, l;
           cur_dist = 0;
           tot_dist = 0;
           // Four different calculations for the different quadrants.
           if(angle > 7 * M_PI_4 || angle <= M_PI_4)
           {
               // Continue while the dist travelled is less than the dist energy
               while(cur_dist < dist)
               {
                   // Check if the starting position of the loop is in the fine map or not.
                   if(checkFine(newx, newy, 0, 0))
                   {
                       // Keep the standard movement rate
                       boost = 1;
                   }
                   else
                   {
                       // Accellerate the travel speed if the point is outside the fine grid.
                       // Note this means that lineages travelling from outside the fine grid to within the
                       // fine grid may
                       // see 1 grid's worth of approximation, rather than exact values.
                       // This is an acceptable approximation!
                       boost = deme;
                   }
   
                   // Add the value to the new x and y values.
                   newx = newx + boost;
                   newy = newy + boost * tan(angle);
                   // Check if the new point is within forest.
                   if(checkMap(newx, newy, 0, 0, generation))
                   {
                       l = 1;
                   }
                   else
                   {
                       l = dispersal_relative_cost;
                   }
                   // Move forward different dists based on the difficulty of moving through forest.
                   cur_dist = cur_dist + l * boost * (1 / cos(angle));
                   tot_dist = tot_dist + boost * (1 / cos(angle));
               }
           }
           else if(angle > 3 * M_PI_4 && angle <= 5 * M_PI_4)
           {
               while(cur_dist < dist)
               {
                   if(checkFine(newx, newy, 0, 0))
                   {
                       boost = 1;
                   }
                   else
                   {
                       boost = deme;
                   }
                   // Add the change to the new x and y values.
                   newx = newx - boost;
                   newy = newy + boost * tan(M_PI - angle);
                   if(checkMap(newx, newy, 0, 0, generation))
                   {
                       l = 1;
                   }
                   else
                   {
                       l = dispersal_relative_cost;
                   }
                   cur_dist = cur_dist + boost * l * (1 / cos(M_PI - angle));
                   tot_dist = tot_dist + boost * (1 / cos(M_PI - angle));
               }
           }
           else if(angle > M_PI_4 && angle <= 3 * M_PI_4)
           {
               while(cur_dist < dist)
               {
                   if(checkFine(newx, newy, 0, 0))
                   {
                       boost = 1;
                   }
                   else
                   {
                       boost = deme;
                   }
                   // Add the change to the new x and y values.
                   newx = newx + boost * tan(angle - M_PI_2);
                   newy = newy + boost;
                   if(checkMap(newx, newy, 0, 0, generation))
                   {
                       l = 1;
                   }
                   else
                   {
                       l = dispersal_relative_cost;
                   }
                   cur_dist = cur_dist + l * boost / cos(angle - M_PI_2);
                   tot_dist = tot_dist + boost / cos(angle - M_PI_2);
               }
           }
           else if(angle > 5 * M_PI_4 && angle <= 7 * M_PI_4)
           {
               //              os << "...ang4..." <<  flush;
               while(cur_dist < dist)
               {
                   if(checkFine(newx, newy, 0, 0))
                   {
                       boost = 1;
                   }
                   else
                   {
                       boost = deme;
                   }
                   newx = newx + boost * tan(3 * M_PI_2 - angle);
                   newy = newy - boost;
                   if(checkMap(newx, newy, 0, 0, generation))
                   {
                       l = 1;
                   }
                   else
                   {
                       l = dispersal_relative_cost;
                   }
                   cur_dist = cur_dist + l * boost / cos(3 * M_PI_2 - angle);
                   tot_dist = tot_dist + boost / cos(3 * M_PI_2 - angle);
               }
           }
           // Move the point back to get the exact placement
           if(checkMap(newx, newy, 0, 0, generation))
           {
               tot_dist = tot_dist - min(cur_dist - dist, (double(boost) - 0.001));
           }
           else
           {
               disp_comp = true;
           }
           newx = startx + 0.5 + tot_dist * cos(angle);
           newy = starty + 0.5 + tot_dist * sin(angle);
       }
       unsigned long ret = getVal(newx, newy, 0, 0, generation);
       if(ret >0)
       {
           long newxwrap, newywrap;
           newxwrap = 0;
           newywrap = 0;
           convertCoordinates(newx, newy, newxwrap, newywrap);
   #ifdef DEBUG
           if(!checkMap(newx, newy, newxwrap, newywrap, generation))
           {
               throw Map_Fatal_Exception(string(
                   "ERROR_MOVE_007: Dispersal attempted to non-forest. Check dispersal function. Forest cover: " +
                   to_string((long long)getVal(newx, newy, newxwrap, newywrap, generation))));
           }
   #endif
           startx = newx;
           starty = newy;
           startxwrap = newxwrap;
           startywrap = newywrap;
           disp_comp = false;
       }
       return ret;
   };
   
   void Map::clearMap()
   {
       dCurrent = 0;
       checksetdim = false;
       bPristine = false;
   }
   
   string Map::printVars()
   {
       stringstream os;
       os << "fine x limits: " << finexmin << " , " << finexmax << endl;
       os << "fine y limits: " << fineymin << " , " << fineymax << endl;
       os << "fine map offset: " << finexoffset << " , " << fineyoffset << endl;
       os << "coarse x limits: " << coarsexmin << " , " << coarsexmax << endl;
       os << "coarse y limits: " << coarseymin << " , " << coarseymax << endl;
       os << "x,y dims: " << xdim << " , " << ydim << endl;
       return os.str();
   }
   
   unsigned long Map::getForestMax()
   {
   #ifdef DEBUG
       if(iForestMax > 10000)
       {
           cerr << "iForestMax is out of whack: " << iForestMax << endl;
           cerr << "fine, coarse, pfine, pcoarse: " << iFineForestMax << ", " << iCoarseForestMax;
           cerr << ", " << iPristineFineForestMax << ", " << iPristineCoarseForestMax << endl;
           throw Fatal_Exception();
       }
   #endif
       return iForestMax;
   }
   
   void Map::recalculateForestMax()
   {
       iForestMax = 0;
       if(bPristine && hasPristine)
       {
           if(iForestMax < iPristineFineForestMax)
           {
               iForestMax = iPristineFineForestMax;
           }
           if(iForestMax < iPristineCoarseForestMax)
           {
               iForestMax = iPristineCoarseForestMax;
           }
       }
       else
       {
           if(iForestMax < iFineForestMax)
           {
               iForestMax = iFineForestMax;
           }
           if(iForestMax < iCoarseForestMax)
           {
               iForestMax = iCoarseForestMax;
           }
           if(iForestMax < iPristineFineForestMax)
           {
               iForestMax = iPristineFineForestMax;
           }
           if(iForestMax < iPristineCoarseForestMax)
           {
               iForestMax = iPristineCoarseForestMax;
           }
       }
       
   }
