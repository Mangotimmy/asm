"""
This format requires HatAsm: https://github.com/EntySec/HatAsm
Current source: https://github.com/EntySec/HatAsm
"""

import struct

from hatasm.lib.format import Format


class HatAsmFormat(Format):
    dll_magic = [
        b"\x4d\x5a"
    ]

    dll_headers = {
        'x86': (
            b'\x4d\x5a\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x00'
            b'\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x0e\x1f\xba\x0e\x00\xb4\x09\xcd'
            b'\x21\xb8\x01\x4c\xcd\x21\x54\x68\x69\x73\x20\x70\x72\x6f\x67\x72\x61\x6d\x20\x63\x61\x6e\x6e\x6f'
            b'\x74\x20\x62\x65\x20\x72\x75\x6e\x20\x69\x6e\x20\x44\x4f\x53\x20\x6d\x6f\x64\x65\x2e\x0d\x0d\x0a'
            b'\x24\x00\x00\x00\x00\x00\x00\x00\x50\x45\x00\x00\x4c\x01\x03\x00\x9e\xa7\xb6\x58\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\xe0\x00\x0e\x23\x0b\x01\x02\x1b\x00\x02\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00'
            b'\x00\x10\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x10\x00\x00\x00\x02\x00\x00'
            b'\x04\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x04\x00\x00'
            b'\xe2\x9e\x00\x00\x03\x00\x00\x00\x00\x00\x20\x00\x00\x10\x00\x00\x00\x00\x10\x00\x00\x10\x00\x00'
            b'\x00\x00\x00\x00\x10\x00\x00\x00\x00\x20\x00\x00\xff\x0e\x00\x00\x00\x30\x00\x00\x14\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2e\x74\x65\x78\x74\x00\x00\x00'
            b'\x54\x01\x00\x00\x00\x10\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x20\x00\x50\x60\x2e\x65\x64\x61\x74\x61\x00\x00\xff\x0e\x00\x00\x00\x20\x00\x00'
            b'\x00\x04\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x30\x40'
            b'\x2e\x69\x64\x61\x74\x61\x00\x00\x14\x00\x00\x00\x00\x30\x00\x00\x00\x02\x00\x00\x00\x0a'
        )
    }

    def __init__(self) -> None:
        super().__init__({
            'Name': 'Dynamic Link Library Format',
            'Description': (
                'Pack machine code into a DLL file.'
            ),
            'Arch': self.dll_headers.keys(),
            'Platform': 'windows'
        })

    def run(self, arch, data):
        filename = 'kernel32.dll'
        dll_inj_funcs = []

        if data[:2] in self.dll_magic:
            return data

        for header_arch in self.dll_headers:
            if arch != header_arch:
                continue

            pe = self.dll_headers[header_arch] + b'\x00' * 546 + data

            if arch == 'x86':
                pe += b'\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff'
                content = pe.ljust(1536, b'\x00')

                content += b'\x00' * 16
                content += b'\x01\x00\x00\x00'
                content += struct.pack('<I', len(dll_inj_funcs)) * 2

                content += b'\x28\x20\x00\x00'
                content += struct.pack('B', 0x28 + len(dll_inj_funcs) * 4) + b'\x20\x00\x00'
                content += struct.pack('B', 0x28 + len(dll_inj_funcs) * 8) + b'\x20\x00\x00'

                content += b'\x00\x10\x00\x00' * len(dll_inj_funcs)
                base = 0x2100 + len(filename) - 1
                content += struct.pack('<H', base) + b'\x00\x00'

                for func_name in dll_inj_funcs[:-1]:
                    base += len(func_name) + 1
                    content += struct.pack('<H', base) + b'\x00\x00'

                for i in range(len(dll_inj_funcs)):
                    content += struct.pack('<H', i)

                content += filename.encode() + b'.dll\x00'
                for func_name in dll_inj_funcs:
                    content += func_name + b'\x00'

                content = content.ljust(3072, b'\x00')
            else:
                raise RuntimeError("DLL header corrupted!")

            return content

        raise RuntimeError("Failed to find compatible DLL header!")
