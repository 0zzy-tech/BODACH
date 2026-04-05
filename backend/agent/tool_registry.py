from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool
from backend.agent.tools.nmap import NmapTool
from backend.agent.tools.gobuster import GobusterTool
from backend.agent.tools.nikto import NiktoTool
from backend.agent.tools.sqlmap import SqlmapTool
from backend.agent.tools.metasploit import MetasploitTool
from backend.agent.tools.hydra import HydraTool
from backend.agent.tools.whatweb import WhatwebTool
from backend.agent.tools.dirb import DirbTool
from backend.agent.tools.wfuzz import WfuzzTool
from backend.agent.tools.enum4linux import Enum4linuxTool
from backend.agent.tools.smbclient_tool import SmbclientTool
from backend.agent.tools.ffuf import FfufTool
from backend.agent.tools.masscan import MasscanTool
from backend.agent.tools.searchsploit import SearchsploitTool
from backend.agent.tools.dnsrecon import DnsreconTool
from backend.agent.tools.theharvester import TheHarvesterTool
from backend.agent.tools.nuclei import NucleiTool
from backend.agent.tools.netexec import NetexecTool
from backend.agent.tools.john import JohnTool
from backend.agent.tools.sslscan import SslscanTool
from backend.agent.tools.impacket_secretsdump import ImpacketSecretsdumpTool
from backend.agent.tools.feroxbuster import FeroxbusterTool
from backend.agent.tools.wpscan import WpscanTool
from backend.agent.tools.kerbrute import KerberuteTool
from backend.agent.tools.impacket_getnpusers import ImpacketGetNPUsersTool
from backend.agent.tools.impacket_getuserspns import ImpacketGetUserSPNsTool
from backend.agent.tools.hashcat import HashcatTool
from backend.agent.tools.snmpcheck import SnmpCheckTool
from backend.agent.tools.commix import CommixTool
from backend.agent.tools.subfinder import SubfinderTool
from backend.agent.tools.medusa import MedusaTool
from backend.agent.tools.msfvenom import MsfvenomTool
from backend.agent.tools.arjun import ArjunTool
# ── Web pentesting tools ──────────────────────────────────────────────────────
from backend.agent.tools.wafw00f import Wafw00fTool
from backend.agent.tools.dalfox import DalfoxTool
from backend.agent.tools.httpx import HttpxTool
from backend.agent.tools.katana import KatanaTool
from backend.agent.tools.gau import GauTool
from backend.agent.tools.jwt_tool import JwtToolTool
from backend.agent.tools.ssrfmap import SsrfmapTool
from backend.agent.tools.smuggler import SmugglerTool
from backend.agent.tools.corscanner import CorsscannerTool
from backend.agent.tools.crlfuzz import CrlfuzzTool
from backend.agent.tools.trufflehog import TrufflehogTool
from backend.agent.tools.gitleaks import GitleaksTool
from backend.agent.tools.eyewitness import EyewitnessTool
from backend.agent.tools.testssl import TestsslTool
from backend.agent.tools.tplmap import TplmapTool
from backend.agent.tools.amass import AmassTool
from backend.agent.tools.dnsx import DnsxTool
from backend.agent.tools.interactsh_client import InteractshClientTool
from backend.agent.tools.linkfinder import LinkfinderTool
from backend.agent.tools.joomscan import JoomscanTool
from backend.agent.tools.dotdotpwn import DotdotpwnTool
from backend.agent.tools.droopescan import DroopescanTool
from backend.agent.tools.s3scanner import S3scannerTool
from backend.agent.tools.kiterunner import KiterunnerTool
from backend.agent.tools.gowitness import GowitnesssTool
from backend.agent.tools.lfimap import LfimapTool
from backend.agent.tools.graphql_cop import GraphqlCopTool
from backend.agent.tools.puredns import PurednsTool
from backend.agent.tools.oralyzer import OralyzerTool
from backend.agent.tools.secretfinder import SecretfinderTool


class ToolRegistry:
    def __init__(self) -> None:
        _tools: list[BaseTool] = [
            # ── Core recon & scanning ─────────────────────────────────────────
            NmapTool(),
            MasscanTool(),
            HttpxTool(),
            WhatwebTool(),
            # ── Web directory & content discovery ─────────────────────────────
            GobusterTool(),
            FfufTool(),
            FeroxbusterTool(),
            DirbTool(),
            # ── Web vulnerability scanning ────────────────────────────────────
            NiktoTool(),
            NucleiTool(),
            Wafw00fTool(),
            # ── Web crawling & URL discovery ──────────────────────────────────
            KatanaTool(),
            GauTool(),
            LinkfinderTool(),
            SecretfinderTool(),
            # ── Injection attacks ──────────────────────────────────────────────
            SqlmapTool(),
            CommixTool(),
            DalfoxTool(),
            TplmapTool(),
            LfimapTool(),
            DotdotpwnTool(),
            CrlfuzzTool(),
            # ── Auth & session attacks ─────────────────────────────────────────
            JwtToolTool(),
            HydraTool(),
            MedusaTool(),
            # ── Protocol & infrastructure attacks ─────────────────────────────
            SsrfmapTool(),
            SmugglerTool(),
            CorsscannerTool(),
            # ── TLS / SSL ──────────────────────────────────────────────────────
            SslscanTool(),
            TestsslTool(),
            # ── CMS scanners ───────────────────────────────────────────────────
            WpscanTool(),
            JoomscanTool(),
            DroopescanTool(),
            # ── API testing ────────────────────────────────────────────────────
            ArjunTool(),
            WfuzzTool(),
            KiterunnerTool(),
            GraphqlCopTool(),
            # ── DNS & subdomain enumeration ────────────────────────────────────
            SubfinderTool(),
            AmassTool(),
            DnsreconTool(),
            DnsxTool(),
            PurednsTool(),
            # ── OSINT & secret discovery ───────────────────────────────────────
            TheHarvesterTool(),
            TrufflehogTool(),
            GitleaksTool(),
            OralyzerTool(),
            # ── Cloud ──────────────────────────────────────────────────────────
            S3scannerTool(),
            # ── Visual recon ───────────────────────────────────────────────────
            EyewitnessTool(),
            GowitnesssTool(),
            # ── OOB / interaction ──────────────────────────────────────────────
            InteractshClientTool(),
            # ── Network & infrastructure ──────────────────────────────────────
            SearchsploitTool(),
            MetasploitTool(),
            MsfvenomTool(),
            # ── Windows / AD ──────────────────────────────────────────────────
            Enum4linuxTool(),
            SmbclientTool(),
            NetexecTool(),
            KerberuteTool(),
            ImpacketGetNPUsersTool(),
            ImpacketGetUserSPNsTool(),
            ImpacketSecretsdumpTool(),
            # ── Password cracking ─────────────────────────────────────────────
            JohnTool(),
            HashcatTool(),
            # ── Other ─────────────────────────────────────────────────────────
            SnmpCheckTool(),
        ]
        self._registry: dict[str, BaseTool] = {t.name: t for t in _tools}

    def get_all_schemas(self) -> list[dict[str, Any]]:
        return [t.to_ollama_schema() for t in self._registry.values()]

    def get_tool(self, name: str) -> BaseTool | None:
        return self._registry.get(name)

    def list_names(self) -> list[str]:
        return list(self._registry.keys())

    def list_descriptions(self) -> str:
        lines = []
        for t in self._registry.values():
            lines.append(f"- {t.name}: {t.description.split('.')[0]}")
        return "\n".join(lines)


tool_registry = ToolRegistry()
