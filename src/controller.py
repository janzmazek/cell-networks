import os
import numpy as np
import yaml
import matplotlib.pyplot as plt

class Controller(object):
    """docstring for Controller."""

    def __init__(self, data, view):
        self.data = data
        self.view = view

        self.view.register(self)

        self.current_number = 0
        self.current_stage = 0
        # 0 = start
        # 1 = import
        # 2 = filter
        # 3 = distribute
        # 4 = binarize

    def import_data(self):
        directory_path = self.view.open_directory()
        if directory_path is None:
            return
        series_number = os.path.basename(directory_path)

        series_location = os.path.join(directory_path, "series" + series_number + ".dat")
        settings_location = os.path.join(directory_path, "settings.yaml")
        # if settings_location is false: load sample settings file

        filtered_location = os.path.join(directory_path, "filtered")
        distributions_location = os.path.join(directory_path, "distributions")
        binarized_location = os.path.join(directory_path, "binarized")
        networks_location = os.path.join(directory_path, "networks")
        analized_location = os.path.join(directory_path, "analized")

        positions_location = os.path.join(directory_path, "positions" + series_number + ".dat")

        series = np.loadtxt(series_location)[:-1,:]
        positions = np.loadtxt(positions_location)
        with open(settings_location, 'r') as stream:
            try:
                settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise(ValueError("Could not open settings file."))
        try:
            self.data.import_data(series, positions, settings)
            self.current_stage = 1
        except:
            print("Something wrong")

        self.draw_fig()

# --------------------------- Button click methods --------------------------- #

    def filter_click(self):
        if self.current_stage == 0:
            return
        if self.data.get_filtered_slow() is not False or self.data.get_filtered_fast() is not False:
            self.current_stage = 2
            self.draw_fig()
        else:
            try:
                self.data.filter()
                self.current_stage = 2
                self.draw_fig()
            except ValueError as e:
                print(e)
            except:
                print("Something wrong")

    def distributions_click(self):
        if self.current_stage == 0:
            return
        elif self.data.get_distributions() is not False:
            self.current_stage = 3
            self.draw_fig()
        else:
            try:
                self.data.compute_distributions()
                self.current_stage = 3
                self.draw_fig()
            except ValueError as e:
                print(e)
            except:
                print("Something wrong")

    def binarize_click(self):
        if self.current_stage == 0:
            return
        if self.data.get_binarized_slow() is not False or self.data.get_binarized_fast() is not False:
            self.current_stage = 4
            self.draw_fig()
        else:
            try:
                self.data.binarize_slow()
                self.data.binarize_fast()
                self.current_stage = 4
                self.draw_fig()
            except ValueError as e:
                print(e)
            except:
                print("Something wrong")

    def previous_click(self):
        if self.current_stage == 0:
            return
        if self.current_number > 0:
            self.current_number -= 1
            self.view.cell_number_text.config(text=self.current_number)
            self.draw_fig()

    def next_click(self):
        if self.current_stage == 0:
            return
        if self.current_number < self.data.get_cells()-1:
            self.current_number += 1
            self.view.cell_number_text.config(text=self.current_number)
            self.draw_fig()

    def exclude_click(self):
        if self.current_stage == 0:
            return
        try:
            self.data.exclude(self.current_number)
        except ValueError as e:
            print(e)
        except:
            print("Something wrong")
        self.draw_fig()

    def unexclude_click(self):
        if self.current_stage == 0:
            return
        try:
            self.data.unexclude(self.current_number)
        except ValueError as e:
            print(e)
        except:
            print("Something wrong")
        self.draw_fig()

    def autoexclude_click(self):
        if self.current_stage == 0:
            return
        try:
            self.data.autoexclude()
        except ValueError as e:
            print(e)
        except:
            print("Something wrong")
        self.draw_fig()


    def draw_fig(self):
        if self.current_stage == 0:
            return
        plt.close()
        if self.current_stage == 1:
            self.view.draw_fig(self.data.plot(self.current_number))
        elif self.current_stage == 2:
            self.view.draw_fig(self.data.plot_filtered(self.current_number))
        elif self.current_stage == 3:
            self.view.draw_fig(self.data.plot_distributions(self.current_number))
        elif self.current_stage == 4:
            self.view.draw_fig(self.data.plot_binarized(self.current_number))

    def edit_settings(self):
        if self.current_stage == 0:
            return
        settings = self.data.get_settings()
        self.view.open_settings_window(settings)

    def apply_parameters_click(self):
        new_settings = self.__get_values(self.view.entries)
        self.data.import_settings(new_settings)
        self.data.reset_computations()
        self.current_stage = 1
        self.draw_fig()

    def __get_values(self, parameter):
        if type(parameter) not in (dict, list):
            return float(parameter.get())
        elif type(parameter) is dict:
            dictionary = {}
            for key in parameter:
                dictionary[key] = self.__get_values(parameter[key])
            return dictionary
        elif type(parameter) is list:
            array = []
            for key in parameter:
                array.append(self.__get_values(key))
            return array
