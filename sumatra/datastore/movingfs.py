"""
Datastore based on files written to the local filesystem, moved to a given location.


:copyright: Copyright 2006-2015 by the Sumatra team, see doc/authors.txt
:license: BSD 2-clause, see LICENSE for details.
"""

from __future__ import with_statement
from __future__ import unicode_literals
import os
import tarfile
import shutil
import logging
import mimetypes
import datetime
from contextlib import closing  # needed for Python 2.6
from sumatra.core import TIMESTAMP_FORMAT, component


from .base import DataItem
from .filesystem import FileSystemDataStore


class MovedDataFile(DataItem):
    """A file-like object, that represents a file"""
    # current implementation just for real files

    def __init__(self, path, store, creation=None):
        self.path = path
        #self.full_path=os.path.join(store.move_store,self.path)
        if os.path.expanduser(store.move_store)!=store.move_store:
            self.full_path=os.path.join(os.path.expanduser(store.move_store), self.path)
        else:
            self.full_path=os.path.join(store.move_store,self.path)
        if os.path.exists(self.full_path):
            moveplace_label = self.path.split(os.path.sep)[0]
            info = self._get_info()
            self.size=info.st_size#os.path.getsize(os.path.join(store.move_store,self.path))
        else:
            raise IOError("File %s does not exist" % self.full_path)
        self.creation = creation or datetime.datetime.fromtimestamp(info.st_mtime).replace(microsecond=0)
        self.name = os.path.basename(self.path)
        self.extension = os.path.splitext(self.name)
        self.mimetype, self.encoding = mimetypes.guess_type(self.path)

    def _get_info(self):
        info = os.stat(self.full_path)
        return info

    def get_content(self, max_length=None):
        f=open(self.full_path,'r')
        if max_length:
            content = f.read(max_length)
        else:
            content = f.read()
        f.close()
        return content

    content = property(fget=get_content)

    @property
    def sorted_content(self):
        raise NotImplementedError


@component
class MovingFileSystemDataStore(FileSystemDataStore):
    """
    Represents a locally-mounted filesystem that stores any new files created
    in it. The root of the data store will generally be a subdirectory of the
    real filesystem.
    """
    data_item_class = MovedDataFile

    def __init__(self, root, movepath):
        super(MovingFileSystemDataStore, self).__init__(root)
        self.move_store = movepath

    def __str__(self):
        return "{0} (moving to {1})".format(self.root, self.move_store)

    def __getstate__(self):
        return {'root': self.root, 'movepath': self.move_store}

    def find_new_data(self, timestamp):
        """Finds newly created/changed data items"""
        new_files = self._find_new_data_files(timestamp)
        label = timestamp.strftime(TIMESTAMP_FORMAT)
        moveplace_paths = self._move(label, new_files)
        return [MovedDataFile(path, self).generate_key()
                for path in moveplace_paths]

    def _move(self, label, files, delete_originals=True):
        """
        Moves files and, by default, deletes the originals.
        """
        if not os.path.exists(os.path.expanduser(self.move_store)):
            os.mkdir(os.path.expanduser(self.move_store))
        direct = os.path.join(os.path.expanduser(self.move_store),label)
        if not os.path.exists(direct):
		    os.mkdir(direct)
        # Moves data files
        moveplace_paths = []
        for file_path in files:
            moveplace_path = os.path.join(label, file_path)
            shutil.copy(os.path.join(self.root, file_path), direct)
            moveplace_paths.append(moveplace_path)
        # Delete original files.
        if delete_originals:
            for file_path in files:
                try:
                    os.remove(os.path.join(self.root, file_path))
                except:
                    print("Could not remove file %s" % file_path)

        self._last_label = label # useful for testing
        return moveplace_paths

    def contains_path(self, path):
        raise NotImplementedError
