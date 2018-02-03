
.. _program_listing_file_SimulateDispersal.cpp:

Program Listing for File SimulateDispersal.cpp
========================================================================================

- Return to documentation for :ref:`file_SimulateDispersal.cpp`

.. code-block:: cpp

   // This file is part of NECSim project which is released under BSD-3 license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #include "SimulateDispersal.h"
   
   void SimulateDispersal::setSequential(bool bSequential)
   {
       is_sequential = bSequential;
   }
   
   void SimulateDispersal::setSizes(unsigned long x, unsigned long y)
   {
       if(!has_set_size)
       {
           density_map.SetSize(y, x);
           has_set_size = true;
       }
       else
       {
           throw Map_Exception("Dimensions of the density map already set.");
       }
   }
   
   void SimulateDispersal::importMaps(string map_file)
   {
       if(has_set_size)
       {
           map_name = map_file;
           if(map_file != "null")
           {
               density_map.import(map_file);
               // Now loop over the density map to find the maximum value
               for(unsigned long i = 0; i < density_map.GetCols(); i ++)
               {
                   for(unsigned long j = 0; j < density_map.GetRows(); j ++)
                   {
                       if(density_map[i][j] > max_density)
                       {
                           max_density = density_map[i][j];
                       }
                   }
               }
           }
           else
           {
               for(unsigned long i = 0; i < density_map.GetRows(); i ++)
               {
                   for(unsigned long j = 0; j < density_map.GetCols(); j ++)
                   {
                       density_map[j][i] = 1;
                   }
               }
           }
           
       }
       else
       {
           throw Map_Fatal_Exception("Dimensions of density map not set before import");
       }
   }
   
   void SimulateDispersal::setDispersalParameters(
       string dispersal_method_in, double sigma_in, double tau_in, double m_prob_in, double cutoff_in,
       string landscape_type)
   {
       random.setDispersalMethod(dispersal_method_in, m_prob_in, cutoff_in);
       random.setDispersalParams(sigma_in, tau_in);
       setLandscapeType(landscape_type);
       dispersal_method = dispersal_method_in;
       sigma = sigma_in;
       tau = tau_in;
       m_prob = m_prob_in;
       cutoff = cutoff_in;
   }
   
   void SimulateDispersal::setLandscapeType(string landscape_type)
   {
       if(landscape_type == "infinite")
       {
           getValFptr = &SimulateDispersal::getEndPointInfinite;
       }
       else if(landscape_type == "closed")
       {
           getValFptr = &SimulateDispersal::getEndPointClosed;
       }
       else if(landscape_type == "tiled")
       {
           getValFptr = &SimulateDispersal::getEndPointTiled;
       }
       else
       {
           throw Fatal_Exception("Landscape type not compatible: " + landscape_type);
       }
   }
   
   void SimulateDispersal::setOutputDatabase(string out_database)
   {
       // Check the file is a database
       if(out_database.substr(out_database.length() - 3) != ".db")
       {
           throw Fatal_Exception("Output database is not a .db file, check file name.");
       }
       // Open our SQL connection to the database
       int o2 = sqlite3_open_v2(out_database.c_str(), &database, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, "unix-dotfile");
       if(o2 != SQLITE_OK && o2 != SQLITE_DONE)
       {
           throw Fatal_Exception("Database file cannot be opened or created.");
       }
   }
   
   void SimulateDispersal::setNumberRepeats(unsigned long n)
   {
       num_repeats = n;
       distances.resize(num_repeats);
   }
   
   void SimulateDispersal::storeCellList()
   {
       unsigned long total = 0;
       // First count the number of density cells and pick a cell size
       for(unsigned long i = 0; i < density_map.GetRows(); i++)
       {
           for(unsigned long j = 0; j < density_map.GetCols(); j++)
           {
               total += density_map[i][j];
           }
       }
   
       cells.resize(total);
       unsigned long ref = 0;
       for(unsigned long i = 0; i < density_map.GetRows(); i++)
       {
           for(unsigned long j = 0; j < density_map.GetCols(); j++)
           {
               for(unsigned long k = 0; k < density_map[i][j]; k++)
               {
                   cells[ref].x = j;
                   cells[ref].y = i;
                   ref ++;
               }
           }
       }
   }
   
   const Cell& SimulateDispersal::getRandomCell()
   {
       unsigned long index = floor(random.d01() * cells.size());   
       return cells[index];
   }
   
   bool SimulateDispersal::getEndPointInfinite(double dist, double angle, Cell &this_cell)
   {
       long newx, newy;
       newx = (long) floor(this_cell.x + 0.5 + dist * cos(angle));
       newy = (long) floor(this_cell.y + 0.5 + dist * sin(angle));
       return newx >= (long) (density_map.GetCols()) || newx > 0 ||
               newy >= (long) (density_map.GetRows()) || newy < 0 ||
              getEndPointTiled(dist, angle, this_cell);
   }
   
   bool SimulateDispersal::getEndPointTiled(double dist, double angle, Cell &this_cell)
   {
       unsigned long newx, newy;
       newx = (unsigned long)floor(this_cell.x + 0.5 + dist * cos(angle)) % density_map.GetCols();
       newy = (unsigned long)floor(this_cell.y + 0.5 + dist * sin(angle)) % density_map.GetRows();
       if(double(density_map[newy][newx]) > (random.d01() * double(max_density)))
       {
           this_cell.x = newx;
           this_cell.y = newy;
           return true;
       }
       else
       {
           return false;
       }
   }
   
   bool SimulateDispersal::getEndPointClosed(double dist, double angle, Cell &this_cell)
   {
       long newx, newy;
       newx = (long) floor(this_cell.x + 0.5 + dist * cos(angle));
       newy = (long) floor(this_cell.y + 0.5 + dist * sin(angle));
       return !(newx >= (long) density_map.GetCols() || newx > 0 ||
               newy >= (long) density_map.GetRows() || newy < 0) &&
              getEndPointTiled(dist, angle, this_cell);
   }
   
   bool SimulateDispersal::getEndPoint(double dist, double angle, Cell &this_cell)
   {
       return (this->*getValFptr)(dist, angle, this_cell);
   }
   
   void SimulateDispersal::runDispersal()
   {
       storeCellList();
       Cell this_cell;
       this_cell = getRandomCell();
       unsigned long dist_ref = 0;
       for(unsigned long i = 0; i < num_repeats; i++)
       {
           if(!is_sequential)
           {
               // This takes into account rejection sampling based on density due to
               // setup process for the cell list
               this_cell = getRandomCell();
           }
           bool fail;
           double dist, angle;
           // Keep looping until we get a valid end point
           do
           {
               // Get a random dispersal distance
               dist = random.dispersal();
               angle = random.direction();
               // Check the end point
               fail = !getEndPoint(dist, angle, this_cell);
           } while(fail); 
           // Now store the output location
           distances[dist_ref] = dist;
           dist_ref++;
       }
   }
   
   void SimulateDispersal::writeDatabase()
   {
       if(database)
       {
           // Do the sql output
           // First create the table
           char* sErrMsg;
           sqlite3_stmt* stmt;
           string create_table = "CREATE TABLE IF NOT EXISTS DISPERSAL_DISTANCES (id INT PRIMARY KEY not null, ";
           create_table += " distance DOUBLE not null);";
           int rc = sqlite3_exec(database, create_table.c_str(), NULL, NULL, &sErrMsg);
           int step;
           if(rc != SQLITE_OK)
           {
               string message = "Could not create DISPERSAL_DISTANCES table in database: ";
               throw Fatal_Exception(message.append(sErrMsg));
           }
           // Now add the objects to the database
           string insert_table = "INSERT INTO DISPERSAL_DISTANCES (id, distance) VALUES (?,?);";
           sqlite3_prepare_v2(database, insert_table.c_str(), strlen(insert_table.c_str()), &stmt, NULL);
           // Start the transaction
           rc = sqlite3_exec(database, "BEGIN TRANSACTION;", NULL, NULL, &sErrMsg);
           if(rc != SQLITE_OK)
           {
               throw Fatal_Exception("Cannot start SQL transaction.");
           }       
           for(unsigned long i = 0; i < distances.size(); i++)
           {
               sqlite3_bind_int(stmt, 1, i);
               sqlite3_bind_double(stmt, 2, distances[i]);
               step = sqlite3_step(stmt);
               time_t start_check, end_check;
               time(&start_check);
               time(&end_check);
               while(step != SQLITE_DONE && (end_check - start_check) < 10)
               {
                   step = sqlite3_step(stmt);
                   time(&end_check);
               }
               if(step != SQLITE_DONE)
               {
                   stringstream ss;
                   ss << "SQLITE error code: " << step << endl;
                   ss << "Could not insert into database." << endl;
                   throw  Fatal_Exception(ss.str());
               }
               sqlite3_clear_bindings(stmt);
               sqlite3_reset(stmt);
           }
           rc = sqlite3_exec(database, "END TRANSACTION;", NULL, NULL, &sErrMsg);
           if(rc != SQLITE_OK)
           {
               string message = "Cannot end the SQL transaction: ";
               throw Fatal_Exception(message.append(sErrMsg));
           }
           // Need to finalise the statement
           rc = sqlite3_finalize(stmt);
           if(rc != SQLITE_OK)
           {
               string message = "Cannot finalise the SQL transaction: ";
               throw Fatal_Exception(message.append(sErrMsg));
           }
           // Now add the parameters
           create_table = "CREATE TABLE IF NOT EXISTS PARAMETERS (id INT PRIMARY KEY not null, ";
           create_table += " sigma DOUBLE not null, tau DOUBLE not null, m_prob DOUBLE not null, cutoff DOUBLE NOT NULL,";
           create_table += "dispersal_method TEXT not null, map_file TEXT not null, seed INT NOT NULL);";
           rc = sqlite3_exec(database, create_table.c_str(), NULL, NULL, &sErrMsg);
           if(rc != SQLITE_OK)
           {
               string message = "Could not create PARAMETERS table in database: ";
               throw Fatal_Exception(message.append(sErrMsg));
           }
           insert_table = "INSERT INTO PARAMETERS VALUES(0, " + to_string((long double)sigma) + "," + to_string((long double)tau) + ", ";
           insert_table += to_string((long double)m_prob) + ", " + to_string((long double)cutoff) + ", '" + dispersal_method + "','";
           insert_table += map_name + "', " + to_string(seed) + ");";
           rc = sqlite3_exec(database, insert_table.c_str(), NULL, NULL, &sErrMsg);
           if(rc != SQLITE_OK)
           {
               string message = "Could not insert into PARAMETERS table in database. \n";
   //          message += "Executed command: " + insert_table + "\n";
               message += "Error: ";
               throw Fatal_Exception(message.append(sErrMsg));
           }
       }
       else
       {
           throw Fatal_Exception("Database connection has not been opened, check programming.");
       }
   }
