import { CheckCircle2, Circle, Loader2, XCircle, Clock } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export interface WorkflowStep {
    id: string;
    name: string;
    description?: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    result?: string;
    error?: string;
}

interface WorkflowProgressProps {
    workflowName: string;
    steps: WorkflowStep[];
    currentStepIndex: number;
    totalSteps: number;
    elapsedMs?: number;
    isCompleted?: boolean;
    isFailed?: boolean;
}

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({
    workflowName,
    steps,
    currentStepIndex,
    totalSteps,
    elapsedMs,
    isCompleted,
    isFailed,
}) => {
    const { t } = useTranslation();
    const getStepIcon = (step: WorkflowStep) => {
        switch (step.status) {
            case 'completed':
                return <CheckCircle2 className="h-5 w-5 text-green-600" />;
            case 'running':
                return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
            case 'failed':
                return <XCircle className="h-5 w-5 text-red-600" />;
            default:
                return <Circle className="h-5 w-5 text-gray-300" />;
        }
    };

    const getStepColor = (step: WorkflowStep) => {
        switch (step.status) {
            case 'completed':
                return 'bg-green-50 border-green-200';
            case 'running':
                return 'bg-blue-50 border-blue-200';
            case 'failed':
                return 'bg-red-50 border-red-200';
            default:
                return 'bg-gray-50 border-gray-200';
        }
    };

    return (
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-blue-600" />
                    <h3 className="font-semibold text-gray-900">{workflowName}</h3>
                </div>
                <div className="text-sm text-gray-500">
                    {currentStepIndex + 1} / {totalSteps}
                    {elapsedMs && <span className="ml-2">({(elapsedMs / 1000).toFixed(1)}s)</span>}
                </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-blue-600 transition-all duration-300"
                        style={{ width: `${((currentStepIndex + 1) / totalSteps) * 100}%` }}
                    />
                </div>
            </div>

            {/* Steps List */}
            <div className="space-y-2">
                {steps.map((step, index) => (
                    <div
                        key={step.id || index}
                        className={`p-3 rounded-lg border transition-all ${getStepColor(step)}`}
                    >
                        <div className="flex items-center gap-3">
                            {getStepIcon(step)}
                            <div className="flex-1">
                                <p className="font-medium text-sm text-gray-900">{step.name}</p>
                                {step.description && (
                                    <p className="text-xs text-gray-600 mt-1">{step.description}</p>
                                )}
                                {step.error && (
                                    <p className="text-xs text-red-600 mt-1">{t('workflowProgress.errorPrefix', { error: step.error })}</p>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Status Footer */}
            {isCompleted && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm font-medium text-green-800">{t('workflowProgress.completed')}</p>
                </div>
            )}
            {isFailed && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm font-medium text-red-800">{t('workflowProgress.failed')}</p>
                </div>
            )}
        </div>
    );
};

export default WorkflowProgress;
