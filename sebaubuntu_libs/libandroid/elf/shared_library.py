#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: Apache-2.0
#

from pathlib import Path
from typing import TYPE_CHECKING

from sebaubuntu_libs.libandroid.elf.elf import ELF

if TYPE_CHECKING:
	from sebaubuntu_libs.libandroid.partitions.partition import AndroidPartition
else:
	AndroidPartition = None

class SharedLibrary:
	def __init__(self,
	             name: str,
	             partition: AndroidPartition,
	            ):
		self.name = name
		self.partition = partition

		self.filename = f"{self.name}.so"

		path_32 = self.partition.path / "lib" / self.filename
		self.lib_32 = ELF(path_32) if path_32.is_file() else None

		path_64 = self.partition.path / "lib64" / self.filename
		self.lib_64 = ELF(path_64) if path_64.is_file() else None

		assert self.lib_32 or self.lib_64, f"Library {self.name} not found in {self.partition.path}"

		if self.is_multilib():
			assert (self.lib_32.needed_libraries == self.lib_64.needed_libraries,
			        f"32-bit and 64-bit versions of {self.name} have different dependencies")

		self.needed_libraries = (self.lib_64.needed_libraries
		                         if self.lib_64
		                         else self.lib_32.needed_libraries)

	def is_multilib(self) -> bool:
		"""Check if this library is multilib (both 32 and 64bit)."""
		return self.lib_32 and self.lib_64

	def get_path(self) -> Path:
		"""Get either 64bit library path if exists, else 32bit one."""
		return self.lib_64.path if self.lib_64 else self.lib_32.path
