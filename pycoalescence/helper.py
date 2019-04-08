"""
Port older simulation outputs to the updated naming conventions. Should not be required by most users.
"""

import sqlite3

from pycoalescence.sqlite_connection import check_sql_table_exist


def update_parameter_names(database):
    """
    Alters the parameters names of SIMULATION_PARAMETERS in the database so that it matches the
    updated naming convention.

    Provided for back-compatibility with older simulations.

    .. note:: If the simulation does not require updating, this function exits silently.

    :param database: the database path to alter the names of

    :return: None

    :rtype: None
    """
    try:
        db = sqlite3.connect(database)
        c = db.cursor()
        if not check_sql_table_exist(db, "SIMULATION_PARAMETERS"):
            raise IOError("Table SIMULATION_PARAMETERS does not exist in database.")
        # Check if the parameters are already updated
        sql_query = (
            "SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
            " sample_size, max_time, dispersal_relative_cost, min_num_species, habitat_change_rate,"
            " gen_since_historical, time_config_file, coarse_map_file, coarse_map_x, coarse_map_y,"
            " coarse_map_x_offset, coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, "
            "fine_map_y, fine_map_x_offset, fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y,"
            "sample_x_offset, sample_y_offset, historical_coarse_map, historical_fine_map, sim_complete, "
            "dispersal_method, m_probability, cutoff, landscape_type, protracted, "
            "min_speciation_gen, max_speciation_gen, dispersal_map FROM SIMULATION_PARAMETERS"
        )
        try:
            c.execute(sql_query)
            db = None
            return
        except sqlite3.Error:
            pass
        sql_query = "ALTER TABLE SIMULATION_PARAMETERS RENAME TO SIM_P_backup; "
        try:
            c.execute(sql_query)
        except sqlite3.Error:  # pragma: no cover
            c.execute("DROP TABLE SIM_P_backup;")
            c.execute(sql_query)
        sql_query = "CREATE TABLE SIMULATION_PARAMETERS(seed INT PRIMARY KEY not null, job_type INT NOT NULL,"
        sql_query += (
            "output_dir TEXT NOT NULL, speciation_rate DOUBLE NOT NULL, sigma DOUBLE NOT NULL,tau DOUBLE NOT NULL,"
            " deme INT NOT NULL, "
        )
        sql_query += (
            "sample_size DOUBLE NOT NULL, max_time INT NOT NULL, dispersal_relative_cost DOUBLE NOT NULL, "
            "min_num_species "
        )
        sql_query += "INT NOT NULL, habitat_change_rate DOUBLE NOT NULL, gen_since_historical DOUBLE NOT NULL, "
        sql_query += (
            "time_config_file TEXT NOT NULL, coarse_map_file TEXT NOT NULL, coarse_map_x INT NOT NULL, "
            "coarse_map_y INT NOT NULL,"
        )
        sql_query += (
            "coarse_map_x_offset INT NOT NULL, coarse_map_y_offset INT NOT NULL, coarse_map_scale DOUBLE NOT "
            "NULL, fine_map_file TEXT NOT NULL, fine_map_x INT NOT NULL,"
        )
        sql_query += "fine_map_y INT NOT NULL, fine_map_x_offset INT NOT NULL, fine_map_y_offset INT NOT NULL, "
        sql_query += "sample_file TEXT NOT NULL, grid_x INT NOT NULL, grid_y INT NOT NULL, sample_x INT NOT NULL, "
        sql_query += "sample_y INT NOT NULL, sample_x_offset INT NOT NULL, sample_y_offset INT NOT NULL, "
        sql_query += (
            "historical_coarse_map TEXT NOT NULL, historical_fine_map TEXT NOT NULL, sim_complete INT NOT NULL, "
        )
        sql_query += "dispersal_method TEXT NOT NULL, m_probability DOUBLE NOT NULL, cutoff DOUBLE NOT NULL, "
        sql_query += "restrict_self INT NOT NULL, landscape_type TEXT NOT NULL, protracted INT NOT NULL, "
        sql_query += (
            "min_speciation_gen DOUBLE NOT NULL, max_speciation_gen DOUBLE NOT NULL, dispersal_map TEXT NOT NULL);"
        )
        c.execute(sql_query)
        try:
            sql_query = (
                "INSERT INTO SIMULATION_PARAMETERS(seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
                " sample_size, max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_historical,"
                " time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, fine_map_x_offset,"
                "fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, sample_x_offset, sample_y_offset, "
                "historical_coarse_map, historical_fine_map, sim_complete, dispersal_method, m_probability, cutoff, "
                "restrict_self, landscape_type, protracted, min_speciation_gen, max_speciation_gen, dispersal_map)"
                " SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
                " sample_size, max_time, dispersal_relative_cost, min_num_species, forest_change_rate, time_since_pristine,"
                " time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, fine_map_x_offset,"
                "fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, sample_x_offset, sample_y_offset, "
                "pristine_coarse_map, pristine_fine_map, sim_complete, dispersal_method, m_probability, cutoff, "
                "restrict_self, infinite_landscape, protracted, min_speciation_gen, max_speciation_gen, dispersal_map FROM SIM_P_backup;"
            )
            c.execute(sql_query)
        except sqlite3.Error:
            # Provide additional support for a different naming convention
            try:
                sql_query = (
                    "INSERT INTO SIMULATION_PARAMETERS(seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
                    " sample_size, max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_historical,"
                    " time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                    "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, fine_map_x_offset,"
                    "fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, sample_x_offset, sample_y_offset, "
                    "historical_coarse_map, historical_fine_map, sim_complete, dispersal_method, m_probability, cutoff, "
                    "restrict_self, landscape_type, protracted, min_speciation_gen, max_speciation_gen, dispersal_map)"
                    " SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
                    " sample_size, max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, time_since_pristine,"
                    " time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                    "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, fine_map_x_offset,"
                    "fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, sample_x_offset, sample_y_offset, "
                    "pristine_coarse_map, pristine_fine_map, sim_complete, dispersal_method, m_probability, cutoff, "
                    "restrict_self, infinite_landscape, protracted, min_speciation_gen, max_speciation_gen, dispersal_map FROM SIM_P_backup;"
                )
                c.execute(sql_query)
            except sqlite3.Error:
                # Provide additional support for a different naming convention
                sql_query = (
                    "INSERT INTO SIMULATION_PARAMETERS(seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
                    " sample_size, max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_historical,"
                    " time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                    "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, fine_map_x_offset,"
                    "fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, sample_x_offset, sample_y_offset, "
                    "historical_coarse_map, historical_fine_map, sim_complete, dispersal_method, m_probability, cutoff, "
                    "restrict_self, landscape_type, protracted, min_speciation_gen, max_speciation_gen, dispersal_map)"
                    " SELECT seed, job_type, output_dir, speciation_rate, sigma, tau, deme,"
                    " sample_size, max_time, dispersal_relative_cost, min_num_species, habitat_change_rate, gen_since_pristine,"
                    " time_config_file, coarse_map_file, coarse_map_x, coarse_map_y, coarse_map_x_offset, "
                    "coarse_map_y_offset, coarse_map_scale, fine_map_file, fine_map_x, fine_map_y, fine_map_x_offset,"
                    "fine_map_y_offset, sample_file, grid_x, grid_y, sample_x, sample_y, sample_x_offset, sample_y_offset, "
                    "pristine_coarse_map, pristine_fine_map, sim_complete, dispersal_method, m_probability, cutoff, "
                    "restrict_self, infinite_landscape, protracted, min_speciation_gen, max_speciation_gen, dispersal_map FROM SIM_P_backup;"
                )
                c.execute(sql_query)
        c.execute("DROP TABLE SIM_P_backup;")
        db.commit()
        db.close()
        db = None
    except sqlite3.Error as soe:  # pragma: no cover
        raise sqlite3.Error("Could not update simulation parameters: {}".format(soe))
