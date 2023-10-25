//
//  ProjectDetail.swift
//  PaperPilot
//
//  Created by 林思行 on 2023/9/24.
//

import SwiftUI
import SwiftUIFlow
import SwiftData

struct ProjectDetail: View {
    @Environment(\.openWindow) private var openWindow
    @Environment(\.modelContext) private var modelContext

    private let copiableProperties: [(String, PartialKeyPath)] = [("Title", \Paper.title),
                                                                  ("Abstract", \Paper.abstract),
                                                                  ("URL", \Paper.url),
                                                                  ("DOI", \Paper.doi)]

    @AppStorage(AppStorageKey.User.loggedIn.rawValue)
    private var loggedIn: Bool = false
    @SceneStorage(SceneStorageKey.Table.customizations.rawValue)
    private var columnCustomization: TableColumnCustomization<Paper>

    @Bindable var project: Project
    @State private var selection = Set<Paper.ID>()
    @State private var sortOrder = [KeyPathComparator(\Paper.formattedCreateTime, order: .reverse)]
    @State private var isShowingEditProjectSheet = false
    @State private var isShowingAddPaperSheet = false
    @State private var isShowingSharePopover = false
    @State private var updating = false
    @State private var progress: Progress?
    @State private var message: String?

    var body: some View {
        Table(project.papers.sorted(using: sortOrder),
              selection: $selection,
              sortOrder: $sortOrder,
              columnCustomization: $columnCustomization
        ) {
            TableColumn("Status") { paper in
                (ModelStatus(rawValue: paper.status) ?? ModelStatus.normal).icon
                    .contentTransition(.symbolEffect(.replace))
            }
            .width(35)
            .alignment(.center)
            .customizationID("status")
            TableColumn("Title", value: \.title)
                .customizationID("title")
                .disabledCustomizationBehavior(.visibility)
            TableColumn("Authors", value: \.formattedAuthors)
                .customizationID("authors")
            TableColumn("Publication Year") { paper in
                Text(paper.publicationYear ?? String(localized: "Unknown"))
            }
            .width(50)
            .customizationID("publicationYear")
            TableColumn("Publication") { paper in
                Text(paper.publication ?? String(localized: "Unknown"))
            }
            .customizationID("publication")
            TableColumn("Date Added", value: \.formattedCreateTime)
                .width(70)
                .customizationID("dateAdded")
            TableColumn("Tags") { paper in
                VFlow(alignment: .leading, spacing: 4) {
                    ForEach(paper.tags, id: \.self) { tag in
                        TagView(text: tag)
                    }
                }
                .clipped()
            }
            .customizationID("tags")
            TableColumn("Read") { paper in
                if paper.read {
                    Image(systemName: "checkmark.circle.fill")
                }
            }
            .width(35)
            .alignment(.center)
            .customizationID("read")
        }
        .contextMenu(forSelectionType: Paper.ID.self) { selectedPapers in
            if !selectedPapers.isEmpty {
                if selectedPapers.count == 1,
                   let paperId = selectedPapers.first,
                   let paper = project.papers.first(where: { $0.id == paperId }) {
                    Menu("Copy Information", systemImage: "doc.on.doc") {
                        ForEach(copiableProperties, id: \.0) { name, keypath in
                            Button(LocalizedStringKey(name)) {
                                if let value = paper[keyPath: keypath] as? String {
                                    setPasteboard(value)
                                }
                            }
                            .disabled(!(paper[keyPath: keypath] is String))
                        }
                    }
                }
                Divider()
                Button("Mark as Read", systemImage: "checkmark.circle.fill") {
                    for paperId in selectedPapers {
                        if let index = project.papers.firstIndex(where: { $0.id == paperId }) {
                            project.papers[index].read = true
                        }
                    }
                }
                Button("Mark as Unread", systemImage: "circle") {
                    for paperId in selectedPapers {
                        if let index = project.papers.firstIndex(where: { $0.id == paperId }) {
                            project.papers[index].read = false
                        }
                    }
                }
                Divider()
                Menu("Delete", systemImage: "trash") {
                    Button("Paper and PDF file", role: .destructive) {
                        handleDeletePaper(papers: selectedPapers, pdfOnly: false)
                    }
                    Button("PDF file only", role: .destructive) {
                        handleDeletePaper(papers: selectedPapers, pdfOnly: true)
                    }
                }
            }
        } primaryAction: { selectedPapers in
            selectedPapers.forEach { paperId in
                let predicate = #Predicate<Paper> {
                    $0.id == paperId
                }
                let descriptor = FetchDescriptor(predicate: predicate)
                try? modelContext.fetchIdentifiers(descriptor).forEach { id in
                    openWindow(id: AppWindow.reader.id, value: id)
                }
            }
        }
        .overlay(alignment: .bottom) {
            if updating || message != nil {
                HStack(spacing: 8) {
                    if updating {
                        if let progress = progress {
                            ProgressView(value: progress.fractionCompleted)
                        } else {
                            ProgressView().controlSize(.small)
                        }
                        Text("Updating...")
                            .foregroundStyle(.secondary)
                    } else if let message = message {
                        Label(message, systemImage: "exclamationmark.triangle.fill")
                            .foregroundColor(.red)
                    }
                }
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(.regularMaterial)
                .transition(.move(edge: .bottom))
            }
        }
        .task(id: project.id) {
            guard project.remoteId != nil else { return }
            withAnimation {
                updating = true
            }
            do {
                for paper in project.papers {
                    switch paper.status {
                    case ModelStatus.waitingForUpload.rawValue:
                        try await paper.upload(to: project)
                    default:
                        break
                    }
                }
                message = nil
            } catch {
                message = String(localized: "Update failed: \(error.localizedDescription)")
            }
            withAnimation {
                updating = false
            }
        }
        .navigationTitle($project.name)
#if os(macOS)
        .navigationSubtitle(project.desc)
#endif
        .toolbar {
            ToolbarItemGroup {
                Spacer()
                Button("Share", systemImage: "square.and.arrow.up") {
                    isShowingSharePopover.toggle()
                }
                .disabled(!loggedIn)
                .popover(isPresented: $isShowingSharePopover, arrowEdge: .bottom) {
                    ShareProjectView(project: project)
                }

                Button("Project Settings", systemImage: "folder.badge.gear") {
                    isShowingEditProjectSheet.toggle()
                }
                .sheet(isPresented: $isShowingEditProjectSheet) {
                    ProjectCreateEditView(edit: true, project: project)
                }

                Button("Add Document", systemImage: "plus") {
                    isShowingAddPaperSheet.toggle()
                }
                .sheet(isPresented: $isShowingAddPaperSheet) {
                    AddPaperView(project: project)
                }
            }
#if !os(macOS)
            ToolbarItem(placement: .navigationBarLeading) {
                EditButton()
            }
#endif
        }
    }

    func handleDeletePaper(papers: Set<Paper.ID>, pdfOnly: Bool) {
        withAnimation {
            updating = true
        }
        progress = Progress(totalUnitCount: Int64(papers.count))
        Task {
            do {
                for paperId in papers {
                    guard let paper = project.papers.first(where: { $0.id == paperId }) else {
                        progress?.completedUnitCount += 1
                        continue
                    }
                    if pdfOnly,
                       let url = paper.localFile,
                       FileManager.default.fileExists(atPath: url.path()) {
                        try FileManager.default.removeItem(at: url)
                        paper.localFile = nil
                        if paper.file != nil {
                            paper.status = ModelStatus.waitingForDownload.rawValue
                        }
                    } else if let dir = try? FilePath.paperDirectory(for: paper),
                              FileManager.default.fileExists(atPath: dir.path()) {
                        try? FileManager.default.removeItem(at: dir)
                    }
                    if !pdfOnly {
                        if project.remoteId != nil, let remoteId = paper.remoteId {
                            _ = try await API.shared.paper.deletePaper(.with { $0.id = remoteId })
                        }
                        modelContext.delete(paper)
                    }
                    progress?.completedUnitCount += 1
                }
                message = nil
            } catch {
                message = error.localizedDescription
            }
            withAnimation {
                updating = false
            }
            progress = nil
        }
    }
}

#Preview {
    ProjectDetail(project: ModelData.project1)
        .modelContainer(previewContainer)
#if os(macOS)
        .frame(width: 800, height: 600)
#endif
}
