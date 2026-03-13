import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
  status: string;
  statusMap: Record<string, { label: string; color: string }>;
  className?: string;
}

export function StatusBadge({ status, statusMap, className }: StatusBadgeProps) {
  const config = statusMap[status];

  if (!config) {
    return (
      <Badge variant="outline" className={className}>
        {status}
      </Badge>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        config.color,
        className
      )}
    >
      {config.label}
    </span>
  );
}
