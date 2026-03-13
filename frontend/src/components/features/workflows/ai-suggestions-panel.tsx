"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Loader2, ArrowRight } from "lucide-react";
import { AiSuggestion } from "@/services/workflows.service";

interface AiSuggestionsPanelProps {
  onGenerate: (description: string) => void;
  onApply: (suggestion: AiSuggestion) => void;
  suggestion?: AiSuggestion | null;
  isGenerating?: boolean;
}

export function AiSuggestionsPanel({
  onGenerate,
  onApply,
  suggestion,
  isGenerating = false,
}: AiSuggestionsPanelProps) {
  const [description, setDescription] = useState("");

  const handleGenerate = () => {
    if (!description.trim()) return;
    onGenerate(description.trim());
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4 text-purple-500" />
          AI Workflow Generator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the workflow you want to create in natural language. For example: 'When a new client is registered, send a welcome email, wait 3 days, then create a follow-up task for the assigned case worker.'"
            rows={4}
            className="resize-none"
          />
          <Button
            onClick={handleGenerate}
            disabled={!description.trim() || isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Workflow
              </>
            )}
          </Button>
        </div>

        {suggestion && (
          <div className="rounded-lg border bg-purple-50/50 p-4 space-y-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h4 className="text-sm font-semibold">
                  {suggestion.workflow_name}
                </h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {suggestion.description}
                </p>
              </div>
              <Badge variant="outline" className="shrink-0">
                {Math.round(suggestion.confidence * 100)}% match
              </Badge>
            </div>

            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">
                Steps ({suggestion.steps.length}):
              </p>
              <div className="flex flex-wrap gap-1">
                {suggestion.steps.map((step, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-1 text-xs bg-background rounded-md px-2 py-1 border"
                  >
                    <span className="font-medium">{step.name}</span>
                    {index < suggestion.steps.length - 1 && (
                      <ArrowRight className="h-3 w-3 text-muted-foreground ml-1" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            <Button
              size="sm"
              onClick={() => onApply(suggestion)}
              className="w-full"
            >
              Apply Suggestion
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
