'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Bell, 
  Briefcase, 
  FileText, 
  ShieldCheck, 
  BarChart3, 
  Settings,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'Cases', href: '/cases', icon: Briefcase },
  { name: 'SARs', href: '/sars', icon: FileText },
  { name: 'Rules', href: '/rules', icon: ShieldCheck },
  { name: 'Analysis', href: '/analysis', icon: BarChart3 },
  { name: 'Reports', href: '/reports', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar = () => {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col bg-[#0f172a] text-white">
      <div className="flex h-16 items-center px-6">
        <Shield className="h-8 w-8 text-blue-500" />
        <span className="ml-3 text-xl font-bold">FraudGuard</span>
      </div>
      <nav className="flex-1 space-y-1 px-4 py-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              prefetch={false}
              className={cn(
                "flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive 
                  ? "bg-blue-600 text-white" 
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold uppercase">
            GR
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium">Gayathri R.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
