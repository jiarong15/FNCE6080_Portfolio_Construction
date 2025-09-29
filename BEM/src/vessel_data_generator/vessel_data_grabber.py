from abc import ABC, abstractmethod


class VesselDataGrabber(ABC):

    @abstractmethod
    def grab_all_vessel_data_by_names(self):
        pass

    @abstractmethod
    def grab_entry_vessel_data_by_names(self):
        pass

    @abstractmethod
    def grab_exit_vessel_data_by_names(self):
        pass
