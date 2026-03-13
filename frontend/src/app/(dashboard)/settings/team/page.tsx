"use client";

import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { DataTable } from "@/components/shared/data-table/data-table";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { type ColumnDef } from "@tanstack/react-table";
import { toast } from "sonner";
import { format } from "date-fns";
import { UserPlus, MoreHorizontal, Mail, Trash2, Shield } from "lucide-react";

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  status: string;
  lastLogin: string | null;
}

const roleStatusMap: Record<string, { label: string; color: string }> = {
  admin: { label: "Admin", color: "bg-purple-100 text-purple-800" },
  manager: { label: "Manager", color: "bg-blue-100 text-blue-800" },
  caseworker: { label: "Case Worker", color: "bg-green-100 text-green-800" },
  viewer: { label: "Viewer", color: "bg-gray-100 text-gray-800" },
};

const memberStatusMap: Record<string, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-green-100 text-green-800" },
  invited: { label: "Invited", color: "bg-yellow-100 text-yellow-800" },
  inactive: { label: "Inactive", color: "bg-gray-100 text-gray-800" },
};

const initialMembers: TeamMember[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john.doe@migrantsbridge.org",
    role: "admin",
    status: "active",
    lastLogin: "2026-03-13T09:30:00Z",
  },
  {
    id: "2",
    name: "Maria Garcia",
    email: "maria.garcia@migrantsbridge.org",
    role: "manager",
    status: "active",
    lastLogin: "2026-03-12T14:20:00Z",
  },
  {
    id: "3",
    name: "Ahmed Hassan",
    email: "ahmed.hassan@migrantsbridge.org",
    role: "caseworker",
    status: "active",
    lastLogin: "2026-03-13T08:15:00Z",
  },
  {
    id: "4",
    name: "Li Wei",
    email: "li.wei@migrantsbridge.org",
    role: "caseworker",
    status: "active",
    lastLogin: "2026-03-11T16:45:00Z",
  },
  {
    id: "5",
    name: "Sarah Johnson",
    email: "sarah.johnson@migrantsbridge.org",
    role: "viewer",
    status: "invited",
    lastLogin: null,
  },
];

export default function TeamSettingsPage() {
  const [members, setMembers] = useState<TeamMember[]>(initialMembers);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("caseworker");
  const [isSending, setIsSending] = useState(false);

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return;
    setIsSending(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const newMember: TeamMember = {
      id: `${Date.now()}`,
      name: inviteEmail.split("@")[0].replace(/[._]/g, " "),
      email: inviteEmail,
      role: inviteRole,
      status: "invited",
      lastLogin: null,
    };
    setMembers((prev) => [...prev, newMember]);
    setIsSending(false);
    setInviteEmail("");
    setInviteRole("caseworker");
    setInviteOpen(false);
    toast.success(`Invitation sent to ${inviteEmail}`);
  };

  const handleRemove = (id: string) => {
    setMembers((prev) => prev.filter((m) => m.id !== id));
    toast.success("Team member removed");
  };

  const columns: ColumnDef<TeamMember, unknown>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => (
        <div>
          <p className="font-medium">{row.original.name}</p>
          <p className="text-xs text-muted-foreground">{row.original.email}</p>
        </div>
      ),
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => (
        <StatusBadge status={row.original.role} statusMap={roleStatusMap} />
      ),
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <StatusBadge status={row.original.status} statusMap={memberStatusMap} />
      ),
    },
    {
      accessorKey: "lastLogin",
      header: "Last Login",
      cell: ({ row }) =>
        row.original.lastLogin ? (
          <span className="text-sm text-muted-foreground">
            {format(new Date(row.original.lastLogin), "MMM d, yyyy HH:mm")}
          </span>
        ) : (
          <span className="text-sm text-muted-foreground">Never</span>
        ),
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Shield className="mr-2 h-4 w-4" />
              Change Role
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Mail className="mr-2 h-4 w-4" />
              Resend Invite
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive"
              onClick={() => handleRemove(row.original.id)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Remove
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Team Management"
        description="Manage team members and their roles"
        actions={
          <Button onClick={() => setInviteOpen(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Invite Member
          </Button>
        }
      />

      <Card>
        <CardContent className="pt-6">
          <DataTable columns={columns} data={members} />
        </CardContent>
      </Card>

      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite Team Member</DialogTitle>
            <DialogDescription>
              Send an invitation email to add a new member to your team.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="invite-email">Email Address</Label>
              <Input
                id="invite-email"
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="colleague@example.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-role">Role</Label>
              <Select value={inviteRole} onValueChange={setInviteRole}>
                <SelectTrigger id="invite-role">
                  <SelectValue placeholder="Select a role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="manager">Manager</SelectItem>
                  <SelectItem value="caseworker">Case Worker</SelectItem>
                  <SelectItem value="viewer">Viewer</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setInviteOpen(false)}
              disabled={isSending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleInvite}
              disabled={!inviteEmail.trim() || isSending}
            >
              <Mail className="mr-2 h-4 w-4" />
              {isSending ? "Sending..." : "Send Invite"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
